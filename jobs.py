from redis_init import rediscl as r, REDIS_KEY_PREFIX
from uuid import uuid4 as uuid, UUID
from datetime import timedelta
from linkcheck import analyze_url
from wikiinteractor import analyze_article
import json
from celery import shared_task
from app import celery as celery_app
from difflib import SequenceMatcher
import re

import re
from difflib import SequenceMatcher

def normalize(title):
    title = title.lower()
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'\|.*$', '', title)
    return title

def title_similarity(title1, title2):
    t1 = normalize(title1)
    t2 = normalize(title2)
    return SequenceMatcher(None, t1, t2).ratio()

MATCH_THRESHOLD = 0.7

@shared_task
def crawl_page(json_data: dict, num: int, rid: UUID) -> None:
    url = json_data['url']
    doi = json_data.get('doi', None)
    json_data['url_info'] = analyze_url(url)
    if doi:
        json_data['doi_info'] = analyze_url(doi)
    json_data['hallucinated'] = json_data['url_info']['hallucinated'] or (json_data['url_info'] and 
        json_data['url_info']['citoid'] and title_similarity(json_data['url_info']['citoid'][0]['title'].strip(), json_data['title'].strip()) < MATCH_THRESHOLD)
    json_data['title_similarity'] = title_similarity(json_data['title'], json_data['url_info']['citoid'][0]['title'].strip()) if json_data['url_info']['citoid'] else 0
    json_data['hallucinated_unsure'] = True if not json_data['url_info']['hallucinated'] and not json_data['url_info']['citoid'] else False
    if doi and 'doi_info' in json_data:
        json_data['hallucinated'] = json_data['hallucinated'] or json_data['doi_info'] == {}
        json_data['hallucinated_doi'] = json_data['hallucinated'] or json_data['doi_info'] == {}
    r.sadd(REDIS_KEY_PREFIX + str(rid), str(num) + '|' + json.dumps(json_data))
    r.expire(REDIS_KEY_PREFIX + str(rid), timedelta(days=1))

@shared_task(ignore_result=False)
def alive(a: int, b:int) -> int:
    return a + b


def push_analysis(article_name: str):
    run_id = uuid()
    article_data = analyze_article(article_name)
    if article_data['exists']:
        citation_data = article_data['template_info']
        count = 0
        for citation in citation_data:
            count += 1
            crawl_page.delay(
                citation,
                count,
                run_id)
        return {
            'exists': article_data['exists'],
            'count': article_data['template_count'],
            'rid': run_id
        }
    return {
        'exists': article_data['exists']
    }


def fetch_analysis(uuid: str):
    all_data = r.smembers(REDIS_KEY_PREFIX + uuid)
    ret = []
    for i in all_data:
        ret.append(json.loads(i.split(b'|', 1)[1]))
    ret.sort(key=lambda x: x['url_info']['priority'] if ('priority' in x['url_info']) else x['url_info']['desc'] )
    return ret
