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
        self.command_queues = []
        self.output_queues = []
        self.client_threads = []
        self.server_threads = []
        self.locks = []
        self.users = []
        self.tables = []
        self.bucket_limit = 20
        self.lookup_count = 10
        self.connections_count = 20
        self.bootstrap_node = Node("bootstrap_node", "127.0.0.1", 5555)
        self.private_nodes_count = 4
        self.public_nodes_count = 1
        self._generate_private_nodes(self.private_nodes_count)
        self._generate_public_nodes(self.public_nodes_count)

    def main(self):
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

        while True:
            self.command_queues[0].append(f"{self.user.node.id} STORE priv2priv")
            time.sleep(1)
            self.command_queues[1].append(f"{self.users[self.private_nodes_count].node.id} STORE priv2pub1")
            time.sleep(1)
            self.command_queues[2].append(f"{self.users[self.private_nodes_count].node.id} STORE priv2pub2")
            time.sleep(1)
            self.command_queues[3].append(f"{self.users[self.private_nodes_count].node.id} STORE priv2pub3")
            time.sleep(1)

    def _generate_private_nodes(self, n):
        default_port = 5555
        for i in range(0, n):
            self.users.append(User(f"private{i}", "127.0.0.1", default_port + i))
            self.locks.append(threading.Lock())
            self.tables.append(RoutingTable(self.users[i].node, self.bootstrap_node, self.bucket_limit, f"nodes{i}.txt",
                                            self.locks[i]))

            self.output_queues.append(deque())
            self.server_threads.append(
                Server(self.users[i].node, self.tables[i], self.output_queues[i], self.lookup_count,
                       self.connections_count))
            self.server_threads[i].start()

            self.command_queues.append(deque())
            self.client_threads.append(
                Client(self.users[i].node, self.tables[i], self.command_queues[i], self.lookup_count))
            self.client_threads[i].start()

    def _generate_public_nodes(self, n):
        default_port = 5555 + self.private_nodes_count + 1
        for i in range(self.private_nodes_count, self.private_nodes_count + n):
            self.users.append(User(f"public{i}", "127.0.0.1", default_port + i, True))
            self.locks.append(threading.Lock())
            self.tables.append(RoutingTable(self.users[i].node, self.bootstrap_node, self.bucket_limit, f"nodes{i}.txt",
                                            self.locks[i]))

            self.output_queues.append(deque())
            self.server_threads.append(
                Server(self.users[i].node, self.tables[i], self.output_queues[i], self.lookup_count,
                       self.connections_count))
            self.server_threads[i].start()

            self.command_queues.append(deque())
            self.client_threads.append(
                Client(self.users[i].node, self.tables[i], self.command_queues[i], self.lookup_count))
            self.client_threads[i].start()

if __name__ == "__main__":
    maincls = Main()
    maincls.main()
