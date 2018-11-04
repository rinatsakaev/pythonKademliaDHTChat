from Helpers.Helper import send_command
import json
import socket
from collections import deque

from Helpers.Helper import socketmanager
from Models.Message import Message
from RoutingTable import RoutingTable
from Models.Node import Node
from Helpers.StoppableThread import StoppableThread


class Server(StoppableThread):
    def __init__(self, node: Node, routing_table: RoutingTable, message_output_queue: deque, lookup_count: int,
                 connections_count: int):
        StoppableThread.__init__(self)
        self.node = node
        self.port = node.port
        self.routing_table = routing_table
        self.lookup_count = lookup_count
        self.messages = message_output_queue
        self.connections_count = connections_count
        self._subscribers_file = "subscribers.txt"
        self.subscribers = self._load_subscribers() if node.is_public else None

    def run(self):
        with socketmanager() as sock:
            sock.bind(('', self.port))
            sock.listen(self.connections_count)
            print("Server has started")
            while True:
                if self.stopped():
                    return
                conn, sender_address = sock.accept()
                print(f"Client connected, ip {sender_address}\r\n")
                data = conn.recv(1024).decode(encoding='utf-8')
                sender_credentials, cmd, payload = data.split(' ')
                print(f"got {cmd} from {sender_credentials}, content: {payload}")
                sender_id, sender_port = sender_credentials.split(':')
                response = self.handle_command(sender_id, sender_address[0], int(sender_port), cmd, payload)
                conn.send(response.encode(encoding="utf-8"))
                conn.close()

    def handle_command(self, sender_id: str, sender_ip, sender_port, cmd, payload: str):
        sender_node = Node(sender_id, sender_ip, sender_port)
        if cmd == "FIND_NODE":
            self.routing_table.add_node(sender_node)
            closest_nodes = self.routing_table.get_closest_nodes(payload, self.lookup_count)
            return json.dumps(closest_nodes, default=lambda x: x.__dict__)

        if cmd == "STORE":
            message = Message(sender_node, payload)
            if self.node.is_public:
                self.send_broadcast(message)
                return "ok"

            self.routing_table.add_node(sender_node)
            self.messages.append(message)
            return "ok"

        if cmd == "PING":
            return "PONG"

        if cmd == "SUBSCRIBE":
            self.routing_table.add_node(sender_node)
            self.add_subscriber(sender_node)
            return "ok"
        if cmd == "UNSUBSCRIBE":
            self.subscribers.remove(sender_node)
            self._update_subscribers_file()

    def has_subscriber(self, node: Node):
        for e in self.subscribers:
            if e.id == node.id:
                return True
        return False

    def send_broadcast(self, message: Message):
        for recipient in self.subscribers:
            if recipient.id != message.sender_node.id:
                send_command(message.sender_node, recipient, "STORE", message.content)

    def _load_subscribers(self):
        subscribers = []
        with open(self._subscribers_file, mode="a+") as f:
            raw_nodes = f.readlines()
            raw_nodes = [x.strip() for x in raw_nodes]
            for raw_node in raw_nodes:
                node_id, ip, port = raw_node.split(':')
                subscribers.append(Node(node_id, ip, int(port)))
        return subscribers

    def add_subscriber(self, node: Node):
        if not self.has_subscriber(node):
            self.subscribers.append(node)
            self._update_subscribers_file()

    def _update_subscribers_file(self):
        with open(self._subscribers_file, mode="w") as f:
            for subscriber in self.subscribers:
                f.write(f"{subscriber.id}:{subscriber.ip}:{subscriber.port}\n")
