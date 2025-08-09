from .auth import authenticatedClientGenerator
from .menu import Menu
from .methods import Methods


class apiInterface(object):
    def __init__(self, username, password, endpoint="https://self.muk.ac.ir", cookie={}):
        self.http_client = authenticatedClientGenerator(
            username=username, password=password, cookie=cookie
            )
        self.methods = Methods(self.http_client)
        self.menu = None
    
    def generateMenu(self):
        self.menu = Menu(self.http_client)
        