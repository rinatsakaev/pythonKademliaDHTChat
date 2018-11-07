import base64
import json
import socket
from Helpers.Helper import send_command
from collections import deque
from Helpers.StoppableThread import StoppableThread
from Helpers.Helper import socketmanager
from Models.Node import Node
from RoutingTable import RoutingTable
from Helpers.Helper import xor
from Helpers.NodeExceptions import NodeNotFoundException

class Client(StoppableThread):
    def __init__(self, node: Node, routing_table: RoutingTable, command_queue: deque, k: int, alpha: int):
        StoppableThread.__init__(self)
        self.node = node
        self.routing_table = routing_table
        self.k = k
        self.alpha = alpha
        self.command_queue = command_queue
        self.queried_nodes = []
        self.min_distance = None
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
            found_nodes = self.routing_table.get_closest_nodes(node_to_search_id, self.alpha)
        else:
            for node in found_nodes:
                self.routing_table.add_node(node)

        found_node = [node for node in found_nodes if node.id == node_to_search_id]
        if len(found_node) is not 0:
            self.queried_nodes = []
            return found_node[0]

        good_nodes = self.get_closest_found_nodes(found_nodes, node_to_search_id)

        if len(good_nodes) == 0:
            nodes_to_request = self.get_not_requested_nodes(found_nodes)
            if len(nodes_to_request) == 0:
                self.queried_nodes = []
                raise NodeNotFoundException(f"Can't find node with id {node_to_search_id}")

            return self.send_find_requests(nodes_to_request[:self.k], node_to_search_id)

        return self.send_find_requests(good_nodes[:self.alpha], node_to_search_id)

    def send_find_requests(self, nodes, node_to_search_id):
        for node in nodes:
            new_nodes = self._send_find_node(node, node_to_search_id)
            self.queried_nodes.append(node)
            return self.find_node(node_to_search_id, new_nodes)

    def get_closest_found_nodes(self, found_nodes: list, node_to_search_id):
        good_nodes = []
        for node in found_nodes:
            if self.min_distance is None or xor(node.id, node_to_search_id) < self.min_distance:
                self.min_distance = xor(node.id, node_to_search_id)
                good_nodes.append(node)
        return good_nodes

    def get_not_requested_nodes(self, nodes):
        n = []
        for node in nodes:
            if len([x for x in self.queried_nodes if x.id == node.id]) == 0:
                n.append(node)
        return n

    def handle_command(self, cmd: str):
        node_id, command, content = cmd.split(' ')
        node = self.find_node(node_id)
        b64_content = base64.b64encode(bytes(content, encoding="utf-8"))
        send_command(self.node, node, command, b64_content.decode("utf-8"))
