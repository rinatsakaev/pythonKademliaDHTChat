from _sha1 import sha1
import socket
import json
from Message import Message


class Node:
    def __init__(self, ip, username):
        self.username = username
        self.bootstrap_node_id = sha1("root".encode("utf-8"))
        self.bootstrap_node_ip = "bootstrap_ip"
        self.id = sha1(username.encode("utf-8"))
        self.ip = ip
        self.port = 9090
        self.routing_table = [
                              [("id0","ip0"),("id1","ip1"),("id2","ip2")],
                              [("id3","ip3")]
                              ]
        self._server_socket = socket.socket()
        self._open_server_connection()
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages = []

    def send_store(self, node_id, data):
        ip = self.discover_node_ip(node_id, None)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, self.port))
        sock.send(bytes(f"STORE {self.username} {data}"))

    def discover_node_ip(self, node_id, found_nodes):
        if len(self.routing_table) == 0:
            if found_nodes is None:
                found_nodes = self._send_find_node(self.bootstrap_node_ip, node_id)
        else:
            if found_nodes is None:
                found_nodes = self._connect_to_neighbour_node(node_id)

        for node in found_nodes:
            bucket = self.routing_table[node.id ^ self.id]
            if not any(tup[0] == node.id for tup in bucket):
                bucket.append((node.id, node.ip))

            if node["id"] == node_id:
                return node["ip"]
        for node in found_nodes:
            self.discover_node_ip(node_id, self._send_find_node(node.ip, node_id))

    def get_closest_nodes(self, node_id, k):
        total_count = 0
        closest_nodes = []
        if len(self.routing_table) == 0:
            raise Exception("Routing table is empty, node id {0}", self.id)
        for bucket in self.routing_table:
            sorted_bucket = sorted(bucket, key=lambda x: x ^ node_id, reverse=True)
            closest_nodes += sorted_bucket
            total_count += len(sorted_bucket)
            if total_count >= k:
                break
        return closest_nodes[:k]

    def _open_server_connection(self):
        self._server_socket.bind(('', self.port))
        self._server_socket.listen(10)
        while True:
            conn, address = self._server_socket.accept()
            print(f"Client connected, ip {address}\r\n")
            data = conn.recv(1024).decode(encoding='utf-8')
            cmd, payload = data.split(' ')
            self.handle_command(cmd, payload)

    def handle_command(self, cmd, payload):
        if cmd == "FIND_NODE":
            closest_nodes = self.get_closest_nodes(payload, 4)
            return json.dumps(closest_nodes)

        if cmd == "STORE":
            sender, content = payload
            self.messages.append(Message(sender, content))

    def _send_find_node(self, recipient_ip, node_id):
        self._client_socket.connect((recipient_ip, self.port))
        self._client_socket.send(bytes(f"FIND_NODE {node_id}"))
        res = self._client_socket.recv(1024)
        return json.loads(res.decode(encoding='utf-8'))

    def _connect_to_neighbour_node(self, node_to_search_id):
        for bucket in self.routing_table:
            sorted_bucket = sorted(bucket, key=lambda x: x ^ node_to_search_id, reverse=True)
            for node in sorted_bucket:
                try:
                    self._client_socket.connect((node[1], self.port))
                    self._client_socket.send(bytes(f"FIND_NODE {node_id}"))
                    res = self._client_socket.recv(1024)
                    return json.loads(res.decode(encoding='utf-8'))
                except OSError:
                    print(f"Cant connect to node id {node[0]}")

