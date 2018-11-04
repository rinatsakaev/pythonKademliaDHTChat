import threading
import time
from collections import deque
from FlaskThread import FlaskThread
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
        self.bootstrap_node = Node("a94a8fe5ccb19ba61c4c0873d391e987982fbbd3", "127.0.0.1", 4444)
        self.login = "test"
        self.port = 4444
        self.ip = "127.0.0.1"
        self.bucket_limit = 20
        self.lookup_count = 10
        self.connections_count = 10
        self.user = User(self.login, self.ip, self.port)
        self.lock = threading.Lock()

        self.routing_table = RoutingTable(self.user.node, self.bootstrap_node, self.bucket_limit, "nodes.txt", self.lock)

        self.messages_output_queue = deque()

        self.server_thread = Server(self.user.node, self.routing_table, self.messages_output_queue, self.lookup_count, self.connections_count)
        self.server_thread.start()

        self.command_input_queue = deque()

        self.flask_thread = FlaskThread(self.command_input_queue, self.messages_output_queue)
        self.flask_thread.start()

        self.client_thread = Client(self.user.node, self.routing_table, self.command_input_queue, self.lookup_count)
        self.client_thread.start()
######
        self.user1 = User("test2", self.ip, self.port+1)
        self.lock1 = threading.Lock()
        self.routing_table1 = RoutingTable(self.user1.node, self.bootstrap_node, self.bucket_limit, "nodes.txt",
                                          self.lock1)

        self.messages_output_queue1 = deque()

        self.server_thread1 = Server(self.user.node, self.routing_table1, self.messages_output_queue1, self.lookup_count,
                                    self.connections_count)
        self.server_thread1.start()

        self.command_input_queue1 = deque()


        self.client_thread1 = Client(self.user1.node, self.routing_table1, self.command_input_queue1, self.lookup_count)
        self.client_thread1.start()

        while True:
            self.command_input_queue1.append(f"{self.user.node.id} STORE new_msg")
            time.sleep(1)

if __name__ == "__main__":
    maincls = Main()
    maincls.main()
