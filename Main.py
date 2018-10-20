import sys

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
        self.register_user()

    def register_user(self):
        self.user.node.discover_node_ip(self.user.node.id, None)


if __name__ == "__main__":
    maincls = Main()
    maincls.main()
