import requests
import logging
from .tools import get_anti_forgery
from bs4 import BeautifulSoup as soup

logger = logging.getLogger(__name__)

class authenticatedClientGenerator(object):
    class loginError(Exception):
        pass

    def __init__(self, username, password, endpoint="https://self.muk.ac.ir", cookie={}):
        self.http_client = requests.session()
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.cookie_login = self.login(cookie=cookie)["from_cookie"]

    def getHttpClient(self):
        return self.http_client

    def isLoggedIn(self):
        login = self.http_client.get(f"{self.endpoint}/api/v0/Credit")
        result = False
        try:
            int(login.text)
            result = True
        except Exception as e:
            result = False
        return {"ok": result, "result": login}
    def login(self, cookie={}):
        if cookie:
            self.http_client.cookies.update(cookie)
            check_login = self.isLoggedIn()
        
            if check_login["ok"]:
                logger.info("login from previous cookies success")
                return {"ok": True, "from_cookie": True, "result": check_login["result"]}
            else:
                logger.info("login from previous cookies failed")
            
        else:
            logger.info("no previous cookie found")
        
        self.http_client.cookies.clear()
        
        # if here, login with cookie in database failed. trying username and password
        
        check_login = self.isLoggedIn()
        initial_request = check_login["result"]

        anti_forgery = get_anti_forgery(initial_request.text)

        login = self.http_client.post(
            f'{self.endpoint}{anti_forgery["loginUrl"]}',
            data={
                "idsrv.xsrf": anti_forgery["antiForgery"]["value"],
                "username": self.username,
                "password": self.password
            }
            )

        input_list = soup(login.text, 'html.parser').find_all("input")
        next_form = {x.get("name"):x.get("value") for x in input_list}
        
        for x in range(3):
            self.http_client.post(self.endpoint, data=next_form)
            if self.isLoggedIn()["ok"]:
                logger.info(f"login success after {x+1} refresh")
                return {"ok": True, "from_cookie": False}
            logger.info(f"login refresh attempt {x+1}")
        logger.error("login failed")
        raise self.loginError
    
    def apiPost(self, cmd, **kwargs):
        logger.debug(f"api method {cmd} called: {kwargs}")
        return self.http_client.post(f"{self.endpoint}/api/v0/{cmd}", **kwargs)
    def apiGet(self, cmd, **kwargs):
        logger.debug(f"api method {cmd} called: {kwargs}")
        return self.http_client.get(f"{self.endpoint}/api/v0/{cmd}", **kwargs)