from _sha1 import sha1
import socket
import json
from collections import defaultdict
from Helper import Helper
from Message import Message

class Node:
    def __init__(self, ip, username):
        self.username = username
        self.bootstrap_node_id = sha1("root".encode("utf-8")).digest()[:2]
        self.bootstrap_node_ip = "bootstrap_ip"
        self.id = sha1(username.encode("utf-8")).hexdigest()[:2]
        self.ip = ip
        self.port = 9090
        self.helper = Helper()
        self.routing_table = self.helper.init_routingtable(self.id)
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages = []

    def send_store(self, node_id, data):
        ip = self.discover_node_ip(node_id, None)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, self.port))
        sock.send(bytes(f"STORE {self.username} {data}", encoding="utf-8"))

    def discover_node_ip(self, node_id, found_nodes):
        if found_nodes is None:
            found_nodes = self._connect_to_neighbour_node(node_id)

        for node in found_nodes:
            self._add_node_to_table(node)

            if node["id"] == node_id:
                return node["ip"]
        for node in found_nodes:
            self.discover_node_ip(node_id, self._send_find_node(node["ip"], node_id))

    def get_closest_nodes(self, node_id: str, k) -> list:
        total_count = 0
        closest_nodes = []
        if len(self.routing_table) == 0:
            raise Exception("Routing table is empty, node id {0}", self.id)
        for bucket, nodes in self.routing_table.items():
            sorted_nodes = sorted(nodes, key=lambda x: self.helper.xor(x["id"], node_id))
            closest_nodes.extend(sorted_nodes)
            total_count += len(sorted_nodes)
            if total_count >= k:
                break
        return closest_nodes[:k]

    def _send_find_node(self, recipient_ip, node_id):
        try:
            self._client_socket.connect((recipient_ip, self.port))
            self._client_socket.send(bytes(f"FIND_NODE {node_id}"))
            res = self._client_socket.recv(1024)
            return json.loads(res.decode(encoding='utf-8'))
        except OSError:
            print(f"Cant connect to node {node_id}")

    def _connect_to_neighbour_node(self, node_to_search_id):
        try:
            self._client_socket.connect((self.bootstrap_node_ip, self.port))
            self._client_socket.send(bytes(f"FIND_NODE {node_to_search_id}", encoding="utf-8"))
            res = self._client_socket.recv(1024)
            print(f"Connected to bootstrap node")
            return json.loads(res.decode(encoding='utf-8'))
        except OSError:
            print(f"Cant connect to bootstrap node")

        for bucket, nodes in self.routing_table.items():
            sorted_nodes = sorted(nodes, key=lambda x: self.helper.xor(x["id"], node_to_search_id))
            for node in sorted_nodes:
                try:
                    self._client_socket.connect((node["ip"], self.port))
                    self._client_socket.send(bytes(f"FIND_NODE {node_to_search_id}", encoding="utf-8"))
                    res = self._client_socket.recv(1024)
                    print(f"Connected to node id {node['id']}")
                    return json.loads(res.decode(encoding='utf-8'))
                except OSError:
                    print(f"Cant connect to node id {node['id']}")
            return self.get_closest_nodes(node_to_search_id, 4)

    def _add_node_to_table(self, node: dict):
        bucket = self.routing_table[self.helper.xor(node["id"], self.id)]
        if len(bucket) == 0 or not any(item["id"] == node["id"] for item in bucket):
            bucket.append(node)