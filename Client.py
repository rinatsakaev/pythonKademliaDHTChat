import base64
import json
import socket
from Helpers.Helper import  send_command
from collections import deque
from Helpers.StoppableThread import StoppableThread
from Helpers.Helper import socketmanager
from Models.Node import Node
from RoutingTable import RoutingTable


class Client(StoppableThread):
    def __init__(self, node: Node, routing_table: RoutingTable, command_queue: deque, lookup_count: int):
        StoppableThread.__init__(self)
        self.node = node
        self.routing_table = routing_table
        self.lookup_count = lookup_count
        self.command_queue = command_queue
        print(f"Client has started.\n"
              f"id: {self.node.id}\n"
              f"ip: {self.node.ip}\n"
              f"port: {self.node.port}")

    def run(self):
        discovered_node = self.find_node(self.node.id)
        if discovered_node.ip != self.node.ip or discovered_node.port != self.node.port:
            raise Exception("This id is already taken")
        while True:
            if self.stopped():
                return
            if len(self.command_queue) > 0:
                cmd = self.command_queue.pop()
                self.handle_command(cmd)

    def _send_find_node(self, node: Node, node_to_search_id: str) -> list:
        with socketmanager(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Connecting to {node.ip}:{node.port} (FIND_NODE)")
            s.connect((node.ip, node.port))
            s.send(bytes(f"{self.node.id}:{self.node.port} FIND_NODE {node_to_search_id}", encoding="utf-8"))
            res = s.recv(1024)
            lst = []
            for str_node in json.loads(res.decode(encoding='utf-8')):
                lst.append(Node(None, None, None).init_from_dict(str_node))
            return lst

    def find_node(self, node_to_search_id: str, found_nodes: list = None) -> Node:
        if found_nodes is None:
            found_nodes = self.routing_table.get_closest_nodes(node_to_search_id, self.lookup_count)
        else:
            for node in found_nodes:
                self.routing_table.add_node(node)

        found_node = [node for node in found_nodes if node.id == node_to_search_id]
        if len(found_node) is not 0:
            return found_node[0]

        for node in found_nodes:
            new_nodes = self._send_find_node(node, node_to_search_id)
            return self.find_node(node_to_search_id, new_nodes)

    def handle_command(self, cmd: str):
        node_id, command, content = cmd.split(' ')
        node = self.find_node(node_id)
        b64_content = base64.b64encode(bytes(content, encoding="utf-8"))
        send_command(self.node, node, command, b64_content.decode("utf-8"))
