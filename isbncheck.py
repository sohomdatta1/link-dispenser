import requests as r
from useragent import USERAGENT
import os

def isbn_exists_in_openlibrary(isbn: str) -> bool | None:
    isbn = isbn.strip().replace("-", "")
    s = r.Session()
    s.cookies.set('session', os.environ.get('OPENLIBRARY_SESSION_COOKIE', ''), domain='.openlibrary.org')
    url = "https://openlibrary.org/api/books"
    params = {
        "bibkeys": f"ISBN:{isbn}",
        "format": "json",
        "jscmd": "data"
    }

    try:
        resp = r.get(url, params=params, headers={
            "User-Agent": USERAGENT
        }, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return bool(data) and f"ISBN:{isbn}" in data
        else:
            return None
    except r.RequestException:
        return None
    
def is_valid_isbn(isbn: str) -> bool:
    isbn = isbn.replace("-", "").replace(" ", "")
    if len(isbn) == 10:
        total = sum((10 - i) * (10 if x == "X" else int(x)) for i, x in enumerate(isbn))
        return total % 11 == 0
    elif len(isbn) == 13:
        total = sum((int(x) * (1 if i % 2 == 0 else 3)) for i, x in enumerate(isbn))
        return total % 10 == 0
    return False