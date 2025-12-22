import logging

logger=logging.getLogger(__name__)

class Methods(object):
    def __init__(self, http_client):
        self.http_client = http_client

    def getCredit(self):
        return self.http_client.apiGet("Credit").text