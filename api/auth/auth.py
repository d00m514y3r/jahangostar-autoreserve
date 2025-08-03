from .tools import *
import requests
import json
import logging
from bs4 import BeautifulSoup as soup
import time

logger = logging.getLogger(__name__)

class authenticatedClientGenerator(object):
    class loginError(Exception):
        pass

    def __init__(self, username, password, endpoint="https://self.muk.ac.ir", cookie={}):
        self.http_client = requests.session()
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.login(cookie=cookie)

    def getHttpClient(self):
        return self.http_client

    def isLoggedIn(self):
        login = self.http_client.get(f"{self.endpoint}/api/v0/Credit")
        result = False
        try:
            print(len(login.text))
            int(login.text)
            result = True
        except Exception as e:
            print(e)
            result = False
        return {"ok": result, "result": login}
    def login(self, cookie={}):
        if cookie:
            self.http_client.cookies.update(cookie)
            check_login = self.isLoggedIn()
        
            if check_login["ok"]:
                logger.info("login from previous cookies success")
                return True
            else:
                logger.info("login from previous cookies failed")
            
        else:
            logger.info("no previous cookie found")
        
        self.http_client.cookies.clear()
        
        # if here, login with cookie in static file failed. trying username and password
        
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

        self.http_client.post(self.endpoint, data=next_form)
        self.http_client.post(self.endpoint, data=next_form)
        self.http_client.post(self.endpoint, data=next_form)
        self.http_client.get(self.endpoint)
        self.http_client.get(self.endpoint)
        self.http_client.get(self.endpoint)

        login_result = self.isLoggedIn()

        if login_result["ok"]:
            logger.info("login success")
        else:
            raise loginError
            logger.error("login failed")
    
    # def storeCookie(self):
    #     with open("staticLogin.txt", "w") as f:
    #         json.dump(dict(self.http_client.cookies), f)
    #     logger.info("saved login cookie into static file")
    
    def loadCookie(self):
        self.http_client.cookies.update(self.cookie)
    
    def apiPost(self, cmd, **kwargs):
        logger.debug(f"api method {cmd} called: {kwargs}")
        return self.http_client.post(f"{self.endpoint}/api/v0/{cmd}", **kwargs)
    def apiGet(self, cmd, **kwargs):
        logger.debug(f"api method {cmd} called: {kwargs}")
        return self.http_client.get(f"{self.endpoint}/api/v0/{cmd}", **kwargs)