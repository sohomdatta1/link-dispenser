import mwparserfromhell as mpfh
import requests as r
from typing import List
import json
import datetime

from linkcheck import analyze_url

from useragent import USERAGENT

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
            'User-Agent': USERAGENT
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
            'User-Agent': 'Wikimedia-Toolforge-Link-Dispenser/1.0'
        },
        timeout=10)
    respjson = resp.json()
    extlinks = respjson['parse']['externallinks']
    oldest_rev_time = get_oldest_revision_time(article_name, lang)

    return {
        "exists": True,
        "text": article['revisions'][0]['slots']['main']['content'], # ????
        "extlinks": extlinks,
        "oldest_rev_time": oldest_rev_time
    }

def get_oldest_revision_time(article_name, lang='en'):
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": article_name,
            "rvlimit": 1,
            "rvdir": "newer",
            "rvprop": "timestamp",
            "format": "json"
        }

        response = r.get(url, params=params, headers={ 'User-Agent': USERAGENT }, timeout=10)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for _, page in pages.items():
            if "revisions" in page:
                return page["revisions"][0]["timestamp"]
        return None

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

def get_archive_date(template: mpfh.nodes.Template) -> str | None:
    if template.has("archive-date"):
        return str(template.get("archive-date").value).strip()
    return None

def get_url_status(template: mpfh.nodes.Template) -> str | None:
    if template.has("url-status"):
        return str(template.get("url-status").value).strip()
    return None


def get_title(template: mpfh.nodes.Template) -> str | None:
    if template.has("chapter"):
        return str(template.get("chapter").value).strip().replace('{{!}}', '|')
    if template.has("title"):
        return str(template.get("title").value).strip().replace('{{!}}', '|')
    if template.has("trans-title"):
        return str(template.get("trans-title").value).strip().replace('{{!}}', '|')
    return None

def get_doi(template: mpfh.nodes.Template) -> str | None:
    if template.has("doi"):
        return f'https://doi.org/{str( template.get("doi").value ).strip()}'
    return None

def get_isbn(template: mpfh.nodes.Template) -> str | None:
    if template.has("isbn"):
        return str(template.get("isbn").value).strip()
    return None


def parse_cite_templates_from_article(text: str, oldest_rev_time: str) -> (List[str], int):
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
                    "id": count,
                    "url": url,
                    "template_name": str(template.name).strip(),
                    "template_url_status": get_url_status(template),
                    "archive_date": get_archive_date(template),
                    "doi": get_doi(template),
                    "input": str(template),
                    "access_date": get_access_date(template),
                    "archive_url": get_archive_url(template),
                    "isbn": get_isbn(template),
                    "title": get_title(template),
                    "publication_date": get_publication_date(template),
                    "article_oldest_rev_time": oldest_rev_time
                })
    return (intresting_templates, count)


def analyze_article(name: str):
    article = get_article_text(name)
    if article['exists']:
        json_data = parse_cite_templates_from_article(article['text'], article['oldest_rev_time'])
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
            data['url_infos'] = analyze_url(data['url'])
        return article
    return article
