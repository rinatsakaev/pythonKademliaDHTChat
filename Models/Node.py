from _sha1 import sha1


class Node:
    def __init__(self,  node_id: str, ip: str, port: int):
        self.ip = ip
        self.id = node_id
        self.port = port
