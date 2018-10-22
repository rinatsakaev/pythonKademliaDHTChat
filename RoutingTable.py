from collections import defaultdict, deque

from Node import Node


def xor(a: str, b: str):
    raw = bytes(ord(x) ^ ord(y) for x, y in zip(a, b))
    return int.from_bytes(raw, byteorder="big")


class RoutingTable:
    def __init__(self, node: Node, bucket_limit: int):
        self.node_id = node.id
        self.bucket_limit = bucket_limit
        self._table = defaultdict(deque)

    def add_node(self, node_to_add: Node):
        distance = xor(self.node_id, node_to_add.id)
        bucket = self._table[distance]
        if len(bucket) < self.bucket_limit:
            bucket.append(node_to_add)
        else:
            if self.ping(bucket[0]):
                pass
            bucket.pop()
            bucket.append(node_to_add)

    def get_closest_nodes(self, node_to_compare: Node, count) -> list:
        closest_nodes = []
        for bucket, nodes in self._table.items():
            sorted_nodes = sorted(nodes, key=lambda x: xor(x.id, node_to_compare.id))
            closest_nodes.extend(sorted_nodes)
            if len(closest_nodes) >= count:
                break
        return closest_nodes[:count]

    def ping(self, node:Node):
        return True