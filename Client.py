import threading
from Node import Node
from RoutingTable import RoutingTable


class Client(threading.Thread):
    def __init__(self, node: Node, bucket_limit: int):
        threading.Thread.__init__(self)
        self.node = node
        self.routing_table = RoutingTable(node, bucket_limit)

    def run(self):
        while True:
            cmd = input("Enter command. Format: node_id:message")
            self.handle_command(cmd)

    def send_store(self, node: Node, data: bytes):
        pass

    def _send_find_node(self, node: Node, node_to_search_id: str) -> list:
        pass

    def find_node(self, node_to_search_id: str) -> Node:

        pass

    def handle_command(self, cmd: str):
        node_id, message = cmd.split(':')
        node = self.find_node(node_id)
        self.send_store(node, message.encode("utf-8"))
        pass