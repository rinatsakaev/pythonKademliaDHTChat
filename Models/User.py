from _sha1 import sha1

from Models.Node import Node


class User:
    def __init__(self, login: str, ip, port):
        self.login = login
        self.node = Node(sha1(bytes(login, encoding='utf-8')).hexdigest(), ip, port)
