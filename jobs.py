from redis_init import rediscl as r, REDIS_KEY_PREFIX
from uuid import uuid4 as uuid, UUID
from datetime import timedelta
from linkcheck import analyze_url
from wikiinteractor import analyze_article
import json
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

mp = get_context('spawn')

exec_pool = ProcessPoolExecutor(max_workers=50, mp_context=mp)


def async_main(json_data: dict, num: int, rid: UUID) -> None:
    url = json_data['url']
    json_data['url_info'] = analyze_url(url)
    r.sadd(REDIS_KEY_PREFIX + str(rid), str(num) + '|' + json.dumps(json_data))
    r.expire(REDIS_KEY_PREFIX + str(rid), timedelta(days=1))


def push_analysis(article_name: str):
    run_id = uuid()
    article_data = analyze_article(article_name)
    citation_data = article_data['template_info']
    count = 0
    futures_list = []
    for citation in citation_data:
        count += 1
        futures_list.append(
            exec_pool.submit(
                async_main,
                citation,
                count,
                run_id))
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
    return ret
