import socket
from collections import defaultdict, deque
import threading
from Models.Node import Node
from Helper import xor
from Helper import socketmanager

class RoutingTable:
    def __init__(self, node: Node, bootstrap_node: Node, bucket_limit: int, file_path: str, lock: threading.Lock):
        self.node_id = node.id
        self.node = node
        self.bucket_limit = bucket_limit
        self.lock = lock
        self._table = defaultdict(deque)
        self._file_path = file_path
        self._load_table(bootstrap_node)

    def add_node(self, node_to_add: Node):
        with self.lock:
            distance = xor(self.node_id, node_to_add.id)
            bucket = self._table[distance]
            if not self.if_in_deque(bucket, node_to_add) and len(bucket) < self.bucket_limit:
                bucket.append(node_to_add)
            else:
                if self.ping(bucket[0]):
                    return
                bucket.pop()
                bucket.append(node_to_add)
            self._update_file()

    def get_closest_nodes(self, node_to_search_id: str, count) -> list:
        closest_nodes = []
        if self.node_id == node_to_search_id:
            return [self.node]
        for bucket, nodes in self._table.items():
            sorted_nodes = sorted(nodes, key=lambda x: xor(x.id, node_to_search_id))
            closest_nodes.extend(sorted_nodes)
            if len(closest_nodes) >= count:
                break
        return closest_nodes[:count]

    def _update_file(self):
        with open(self._file_path, mode="w") as f:
            for bucket, nodes in self._table.items():
                for node in nodes:
                    f.write(f"{node.id}:{node.ip}:{node.port}\n")

    def ping(self, node: Node):
        return True

    def _load_table(self, bootstrap_node: Node):
        self.add_node(bootstrap_node)
        self.add_node(self.node)
        with open(self._file_path, mode="a+") as f:
            raw_nodes = f.readlines()
        raw_nodes = [x.strip() for x in raw_nodes]
        for raw_node in raw_nodes:
            node_id, ip, port = raw_node.split(':')
            self.add_node(Node(node_id, ip, int(port)))

    def if_in_deque(self, queue, node:Node):
        lst = list(queue)
        for e in lst:
            if e.id == node.id:
                return True
        return False