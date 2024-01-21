import mwparserfromhell as mpfh
import requests as r
from typing import List
import json
import datetime

from linkcheck import analyze_url

def get_article_text( article_name, lang='en'):
    resp = r.get(f'https://{lang}.wikipedia.org/wiki/{article_name}?action=raw', timeout= 10)

    if resp.status_code != 200:
        return {
            "exists": False
        }

    return {
        "exists": True,
        "text": resp.text
    }

def check_if_has_url( template: mpfh.nodes.Template ) -> str|None:
    if template.has("chapter-url"):
        return str ( template.get("chapter-url").value ).strip()
    if template.has("url"):
        return str( template.get("url").value ).strip()
    if template.has("doi"):
        return f'https://doi.org/{str( template.get("doi").value ).strip()}'
    return None

def get_access_date( template: mpfh.nodes.Template ) -> str|None:
    if template.has("access-date"):
        return str( template.get("access-date").value ).strip()
    return None

def get_publication_date( template: mpfh.nodes.Template ) -> str|None:
    if template.has("date"):
        return str( template.get("date").value ).strip()
    return None

def get_archive_url( template: mpfh.nodes.Template ) -> str|None:
    if template.has("archive-url"):
        return str( template.get("archive-url").value ).strip()
    return None

def get_title( template: mpfh.nodes.Template ) -> str|None:
    if template.has("title"):
        return str( template.get("title").value ).strip().replace( '{{!}}', '|' )

def parse_cite_templates_from_article( text: str ) -> List[str]:
    wikicode = mpfh.parse( text )
    templates = wikicode.filter_templates()
    intresting_templates = []
    for template in templates:
        if  str( template.name ).lower().startswith("cite "):
            url = check_if_has_url(template)
            if url and str( url ).startswith('http'):
                intresting_templates.append( {
                    "url": url,
                    "input": str( template ),
                    "access-date": get_access_date( template ),
                    "archive_url": get_archive_url( template ),
                    "title": get_title( template ),
                    "publication_date": get_publication_date( template )
                } )
    return intresting_templates

def analyze_article( name: str ):
    article = get_article_text(name)
    if article['exists']:
        json_data = parse_cite_templates_from_article( article['text'] )
        article['text'] = ''
        article['template_info'] = json_data
        for data in json_data:
            access_date = data['access-date'] or str( datetime.datetime.utcnow().strftime( '%d-%m-%Y' ) )
            data['url_infos'] = analyze_url(data['url'])
        return article
    return article