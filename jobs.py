from redis_init import rediscl as r, REDIS_KEY_PREFIX
from uuid import uuid4 as uuid, UUID
from datetime import timedelta
from linkcheck import analyze_url
from wikiinteractor import analyze_article
import json
from celery import shared_task
from app import celery as celery_app

@shared_task
def crawl_page(json_data: dict, num: int, rid: UUID) -> None:
    url = json_data['url']
    json_data['url_info'] = analyze_url(url)
    r.sadd(REDIS_KEY_PREFIX + str(rid), str(num) + '|' + json.dumps(json_data))
    r.expire(REDIS_KEY_PREFIX + str(rid), timedelta(days=1))


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


def fetch_analysis(uuid: str):
    all_data = r.smembers(REDIS_KEY_PREFIX + uuid)
    ret = []
    for i in all_data:
        ret.append(json.loads(i.split(b'|', 1)[1]))
    ret.sort(key=lambda x: x['url_info']['priority'] if ('priority' in x['url_info']) else x['url_info']['desc'] )
    return ret
