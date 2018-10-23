import threading
import socket
import json
from Helper import socketcontext
from Models.Message import Message
from RoutingTable import RoutingTable
from Models.Node import Node


class Server(threading.Thread):
    def __init__(self, node: Node, routing_table: RoutingTable, lookup_count: int):
        threading.Thread.__init__(self)
        self.node = node
        self.port = node.port
        self.routing_table = routing_table
        self.lookup_count = lookup_count
        self.messages = []

    def run(self):
        with socketcontext() as sock:
            sock.bind(('', self.port))
            sock.listen(10)
            print("Server has started")
            while True:
                conn, sender_address = sock.accept()
                print(f"Client connected, ip {sender_address}\r\n")
                data = conn.recv(1024).decode(encoding='utf-8')
                sender_credentials, cmd, payload = data.split(' ')
                print(sender_credentials)
                sender_id, sender_port = sender_credentials.split(':')
                response = self.handle_command(sender_id, sender_address[0], sender_port, cmd, payload)
                conn.send(response.encode(encoding="utf-8"))

    def handle_command(self, sender_id: str, sender_ip, sender_port, cmd, payload: str):
        sender_node = Node(sender_id, sender_ip, sender_port)
        self.routing_table.add_node(sender_node)
        if cmd == "FIND_NODE":
            closest_nodes = self.routing_table.get_closest_nodes(payload, self.lookup_count)
            return json.dumps(closest_nodes)

        if cmd == "STORE":
            self.messages.append(Message(sender_node, payload))
            return json.dumps("ok")
