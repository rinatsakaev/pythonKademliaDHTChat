from _sha1 import sha1
from collections import defaultdict
class Helper:
    def __init__(self):
        pass

    def init_routingtable(self, host_node_id: str):
        with open("nodes.txt", mode="r") as f:
            raw_nodes = f.readlines()
        raw_nodes = [x.strip() for x in raw_nodes]
        res = defaultdict(list)
        for raw_node in raw_nodes:
            node_id, ip = raw_node.split(':')
            node = {"id": node_id,
                    "ip": ip}
            res[self.xor(node_id, host_node_id)].append(node)
        return res


