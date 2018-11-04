class Node:
    def __init__(self, node_id: str, ip: str, port: int, is_public: bool = False):
        self.ip = ip
        self.id = node_id
        self.port = port
        self.is_public = is_public

    def init_from_dict(self, d):
        for key, value in d.items():
                setattr(self, key, value)
        return self
