import requests as r
import json
from urllib.parse import urlparse as parse_url
from socket import getaddrinfo, gaierror
from waybackpy import WaybackMachineCDXServerAPI, WaybackMachineSaveAPI, exceptions as wbpye
from dateutil import parser as date_parser
from uuid import uuid4


headers = json.load(open('headers.json', encoding='utf-8'))
ia_useragent = 'Wikimedia_Link_Dispenser/1.0'


def get_url_status_info( url: str ) -> dict:
    try:
        resp = r.get(url, headers=headers, timeout= 60)
    except r.exceptions.ConnectionError as _:
        return {
            "status": 1337,
            "url": url,
            "history": [],
            "description": 'ConnectionError'
        }
    except Exception as _:
        return {
            "status": 1337,
            "url": url,
            "history": [],
            "description": 'Other error'
        }
    history = []
    for i in range( 1, len( resp.history ) ):
        res = resp.history[i-1]
        history.append( {
            "url": res.url,
            "status": res.status_code
        } )

    if len( resp.history ) == 1:
        history.append( {
            "url": resp.history[0].url,
            "status": resp.status_code
        } )
    
    if len( history ) > 0:
        history[ len(history) - 1 ]['url'] = resp.url

    status_code = history[0]['status'] if len( history ) > 0 and resp.status_code == 200  else resp.status_code
    return {
        "status": status_code,
        "url": url,
        "history": history
    }

def get_dns_info( url: str ) -> dict:
    u = parse_url(url)

    try:
        getaddrinfo(u.hostname, u.port or 443)
    except gaierror:
        return {
            "status": 0
        }
    
    return {
        "status": 1
    }

def save_iarchive_url( url: str ) -> dict:
    ia_save_server_api = WaybackMachineSaveAPI(url, ia_useragent)
    try:
        url = ia_save_server_api.save()
    except wbpye.MaximumSaveRetriesExceeded as _:
        return {
            "status": 0
        }
    return {
        "status": 1,
        "archive_url": url,
        "timestamp": ia_save_server_api.timestamp()
    }


def get_iarchive_data( url: str, date: int ) -> dict:
    ia_cdx_server_api = WaybackMachineCDXServerAPI(url, ia_useragent)

    try:
        near = ia_cdx_server_api.near(unix_timestamp=date)
    except wbpye.NoCDXRecordFound as _:
        return {
            "status": 0
        }
    except Exception as _:
        return {
            "status": 0
        }
    return {
        "status": 1,
        "archive_url": near.archive_url,
        "timestamp": near.datetime_timestamp.timestamp(),
    }

def could_be_spammy( url_resp: dict ):
    if len( url_resp['history'] ) == 0:
        return False
    
    start_url_netloc = parse_url( url_resp['history'][0]['url'] ).netloc

    # doi will generally not be spam??
    if str( start_url_netloc ).endswith( 'doi.org' ):
        return False
    
    for resp in url_resp['history']:
        curr_resp_netloc = parse_url( resp['url'] ).netloc
        if not curr_resp_netloc.startswith( start_url_netloc ):
            return True
    return False



def analyze_url( url: str, timestamp: str ) -> dict:
    #tm = date_parser.parse(timestamp)
    json_data = get_url_status_info(url)
    json_data['spammy'] = could_be_spammy(json_data)
    json_data['uid'] = uuid4()
    if json_data['status'] == 200 and not json_data['spammy']:
        json_data['desc'] = 'ok'
    elif json_data['status'] > 399 and json_data['status'] != 1337:
        json_data['desc'] = 'down'
    elif ( ( json_data['status'] > 300 and json_data['status'] < 399) or len( json_data['history'] ) != 0 ) and not json_data['spammy']:
        json_data['desc'] = 'redirect'
    elif json_data['spammy']:
        json_data['desc'] = 'spammy'
    else:
        json_data['desc'] = 'dead'
    json_data['ok'] = json_data['status'] == 200 or json_data['spammy']
    if json_data['status'] > 399 or json_data['spammy']:
        json_data['dns'] = bool( get_dns_info(url)['status'] )
        json_data['archives'] = {
            "status": 0
        }
        #get_iarchive_data(url, int( tm.timestamp() ))
    else:
        json_data['archives'] = {
            "status": 0
        }
    return json_data