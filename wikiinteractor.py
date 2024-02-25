import mwparserfromhell as mpfh
import requests as r
from typing import List
import json
import datetime

from linkcheck import analyze_url


def get_article_text(article_name, lang='en'):
    resp = r.post(
        f'https://{lang}.wikipedia.org/w/api.php',
        data={
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": article_name,
            "formatversion": "2",
            "rvprop": "content",
            "rvslots": "main"
        },
        headers={
            'X-Useragent-Header': 'Wikimedia-Toolforge-Link-Dispenser/1.0'
        },
        timeout=10)

    respjson = resp.json()
    article = respjson['query']['pages'][0]
    if 'missing' in article:
        return {
            "exists": False
        }
    resp = r.post(
        f'https://{lang}.wikipedia.org/w/api.php',
        data={
            "action": "parse",
            "format": "json",
            "page": article_name,
            "prop": "externallinks",
            "formatversion": "2"
        },
        headers={
            'X-Useragent-Header': 'Wikimedia-Toolforge-Link-Dispenser/1.0'
        },
        timeout=10)
    respjson = resp.json()
    extlinks = respjson['parse']['externallinks']

    return {
        "exists": True,
        "text": article['revisions'][0]['slots']['main']['content'], # ????
        "extlinks": extlinks
    }

def check_if_has_url(template: mpfh.nodes.Template) -> str | None:
    if template.has("chapter-url"):
        return str(template.get("chapter-url").value).strip()
    if template.has("url"):
        return str(template.get("url").value).strip()
    if template.has("doi"):
        return f'https://doi.org/{str( template.get("doi").value ).strip()}'
    return None


def get_access_date(template: mpfh.nodes.Template) -> str | None:
    if template.has("access-date"):
        return str(template.get("access-date").value).strip()
    return None


def get_publication_date(template: mpfh.nodes.Template) -> str | None:
    if template.has("date"):
        return str(template.get("date").value).strip()
    return None


def get_archive_url(template: mpfh.nodes.Template) -> str | None:
    if template.has("archive-url"):
        return str(template.get("archive-url").value).strip()
    return None


def get_title(template: mpfh.nodes.Template) -> str | None:
    if template.has("title"):
        return str(template.get("title").value).strip().replace('{{!}}', '|')


def parse_cite_templates_from_article(text: str) -> (List[str], int):
    wikicode = mpfh.parse(text)
    templates = wikicode.filter_templates()
    intresting_templates = []
    count = 0
    for template in templates:
        if str(template.name).lower().startswith(("cite", "citation")):
            url = check_if_has_url(template)
            if url and str(url).startswith('http'):
                count += 1
                intresting_templates.append({
                    "url": url,
                    "input": str(template),
                    "access-date": get_access_date(template),
                    "archive_url": get_archive_url(template),
                    "title": get_title(template),
                    "publication_date": get_publication_date(template)
                })
    return (intresting_templates, count)


def analyze_article(name: str):
    article = get_article_text(name)
    if article['exists']:
        json_data = parse_cite_templates_from_article(article['text'])
        article['text'] = ''
        article['template_info'] = json_data[0]
        article['template_count'] = json_data[1]
        return article
    return article


def analyze_article_and_urls(name: str):
    article = analyze_article(name)
    if article['exists']:
        json_data = article['template_info']
        for data in json_data:
            access_date = data['access-date'] or str(
                datetime.datetime.utcnow().strftime('%d-%m-%Y'))
            data['url_infos'] = analyze_url(data['url'])
        return article
    return article
