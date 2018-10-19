from Node import Node


class User:
    def __init__(self, login, ip):
        self.login = login
        self.node = Node(ip, login)
