from _sha1 import sha1


class Node:
    def __init__(self,  username: str, ip: str, port: int):
        self.ip = ip
        self.username = username
        self.id = sha1(username.encode("utf-8")).hexdigest()
        self.port = port
