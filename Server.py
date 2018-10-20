import threading
import socket
import json

from Message import Message
from Node import Node


class Server(threading.Thread):
    def __init__(self, node: Node):
        threading.Thread.__init__(self)
        self.sock = socket.socket()
        self.node = node
        self.port = 9090

    def run(self):
        self.sock.bind(('', self.port))
        self.sock.listen(10)
        print("Server has started")
        while True:
            conn, address = self.sock.accept()
            print(f"Client connected, ip {address}\r\n")
            data = conn.recv(1024).decode(encoding='utf-8')
            cmd, payload = data.split(' ')
            response = self.handle_command(cmd, payload)
            conn.send(response.encode(encoding="utf-8"))

    def handle_command(self, cmd, payload: str):
        if cmd == "FIND_NODE":
            closest_nodes = self.node.get_closest_nodes(payload, 4)
            return json.dumps(closest_nodes)

        if cmd == "STORE":
            sender, content = payload
            self.node.messages.append(Message(sender, content))