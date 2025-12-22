from urllib import parse
from bs4 import BeautifulSoup as soup
from html import unescape
from json import loads

# def get_arguemnts_from_ul(url, args=('client_id', 'state', 'nonce')):
#     result = {}
#     query_def = parse.parse_qs(
#         parse.urlparse(url)
#         .query)
    
#     for x in args:
#         result[x] = query_def[x][0]
#     return result

def get_anti_forgery(response):
    ll = soup(response, "html.parser")
    payload = ll.find(id="modelJson")
    if payload:
        return loads(unescape(payload.string))
    else:
        return None
# def check_if_form(response):    
#     if "Submit this form" not in response:
#         return False
#     ll = soup(response, "html.parser")
#     x = soup.find_all("input")
#     print(x)
        
