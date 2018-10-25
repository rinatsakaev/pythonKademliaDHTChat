import threading
from collections import deque
from Client import Client
from Models.Node import Node
from RoutingTable import RoutingTable
from Server import Server
from Models.User import User

class Main:
    def __init__(self):
        self.user = None
        self.login = None

    def main(self):
        self.bootstrap_node = Node()
        self.login = input("Enter login")
        self.port = 4444
        self.ip = "127.0.0.1"
        self.bucket_limit = 20
        self.lookup_count = 10
        self.user = User(self.login, self.ip, self.port)
        self.lock = threading.Lock()
        self.routing_table = RoutingTable(self.user.node, self.bucket_limit, "nodes.txt", self.lock)
        self.server_thread = Server(self.user.node, self.routing_table, self.lookup_count)
        self.server_thread.start()
        self.command_queue = deque()
        self.client_thread = Client(self.user.node, self.routing_table, self.command_queue, self.lookup_count)
        self.client_thread.start()

if __name__ == "__main__":
    maincls = Main()
    maincls.main()
