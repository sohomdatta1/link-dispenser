import re
import tldextract
import requests
from useragent import USERAGENT
from redis_init import REDIS_KEY_PREFIX, rediscl
import json

REVIDS_URL = "https://gitlab-content.toolforge.org/kevinpayravi/cite-unseen-revids/-/raw/main/revids.json?mime=text/plain"
API_URL = "https://meta.wikimedia.org/w/api.php"

CACHE_KEY = f"{REDIS_KEY_PREFIX}:cite_unseen_rules"
CACHE_TTL = 86400  # 1 day in seconds

# Map of source to policy page
CITE_UNSEEN_SOURCE_TO_PAGE = {
    'enAs': 'en:Wikipedia:WikiProject Albums/Sources',
    'enAms': 'en:Wikipedia:WikiProject Anime and manga/Online reliable sources',
    'enJapans': 'en:Wikipedia:WikiProject Japan/Reliable sources',
    'enKoreas': 'en:Wikipedia:WikiProject Korea/Reliable sources',
    'enNppsg': 'en:Wikipedia:New pages patrol source guide',
    'enRsp': 'en:Wikipedia:Reliable sources/Perennial sources',
    'enVgs': 'en:Wikipedia:WikiProject Video games/Sources',
    'zhAcgs': 'zh:维基专题:ACG/來源考量',
    'zhRsp': 'zh:维基百科:可靠来源/常见有争议来源列表',
    'zhVgs': 'zh:维基专题:电子游戏/来源考量'
}

def fetch_revids():
    try:
        r = requests.get(REVIDS_URL, headers={ 'User-Agent': USERAGENT }, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def fetch_wikitext_from_revisions(revids):
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "revids": "|".join(map(str, revids)),
        "rvslots": "*",
        "rvprop": "content",
        "formatversion": "2"
    }
    r = requests.get(API_URL, headers={ 'User-Agent': USERAGENT }, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    texts = []
    for page in data["query"]["pages"]:
        if "revisions" in page:
            texts.append(page["revisions"][0]["slots"]["main"]["content"])
    return "\n\n".join(texts)

def split_sections(fulltext):
    sections = {}
    header_regex = re.compile(r"^==[=]+\s*(.*?)\s*===", re.M)
    matches = list(header_regex.finditer(fulltext))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(fulltext)
        sections[m.group(1).strip()] = fulltext[start:end].strip()
    return sections

def parse_culink_templates(section_text):
    pattern = re.compile(r"{{\s*CULink\s*\|\s*([^}]+?)\s*}}")
    matches = pattern.findall(section_text)
    rules = []
    for m in matches:
        parts = [p.strip() for p in m.split("|") if p.strip()]
        rule = {}
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                rule[k.strip()] = v.strip()
        rules.append(rule)
    return rules

def build_rule_index(fulltext):
    sections = split_sections(fulltext)
    categorized_rules = {}
    for section, text in sections.items():
        rules = parse_culink_templates(text)
        if rules:
            categorized_rules.setdefault(section, []).extend(rules)
    return categorized_rules

def normalize_domain(url):
    ext = tldextract.extract(url)
    return ".".join(part for part in [ext.domain, ext.suffix] if part)

def annotate_url_impl(url, rules_index):
    domain = normalize_domain(url)
    annotations = {
        "url": url,
        "domain": domain,
        "tags": [],
        "sourcePage": []
    }
    for section, rules in rules_index.items():
        for rule in rules:
            if "url" in rule and domain in rule["url"]:
                annotations["tags"].append(section)
                for prefix, page_link in CITE_UNSEEN_SOURCE_TO_PAGE.items():
                    if section.startswith(prefix):
                        annotations["sourcePage"].append(page_link)
                        break
    return annotations

def build_index_and_cache():
    revids_data = fetch_revids()
    if not revids_data:
        return None
    revids = revids_data.get("revids", [])
    if not revids:
        return None
    fulltext = fetch_wikitext_from_revisions(revids)
    rules_index = build_rule_index(fulltext)
    rediscl.setex(CACHE_KEY, CACHE_TTL, json.dumps(rules_index))
    return rules_index

def annotate_url(url) -> dict:
    cache_key = f"{CACHE_KEY}:cite_unseen:{url}"
    cached = rediscl.get(cache_key)
    if cached:
        return json.loads(cached)
    
    rules_index_raw = rediscl.get(CACHE_KEY)
    if rules_index_raw:
        rules_index = json.loads(rules_index_raw)
    else:
        rules_index = build_index_and_cache()
        if rules_index is None:
            return {
                "url": url,
                "domain": normalize_domain(url),
                "tags": [],
                "sourcePage": []
            }

    annotations = annotate_url_impl(url, rules_index)
    rediscl.setex(cache_key, CACHE_TTL, json.dumps(annotations))
    return annotations

def annotate_url_with_custom_rules(url: str, custom_rules: dict) -> dict:
    return annotate_url_impl(url, custom_rules)
