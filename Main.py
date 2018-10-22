import sys

from Client import Client
from Server import Server
from User import User




class Main:
    def __init__(self):
        self.user = None
        self.login = None

    def main(self):
        self.login = "rinat"
        self.user = User(self.login, "current_ip")
        self.server_thread = Server(self.user.node)
        self.server_thread.start()
        self.client_thread = Client(self.user.node, 20)
        self.client_thread.start()

if __name__ == "__main__":
    maincls = Main()
    maincls.main()
