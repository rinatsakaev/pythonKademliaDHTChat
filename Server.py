import json
from Helper import socketmanager
from Models.Message import Message
from RoutingTable import RoutingTable
from Models.Node import Node
from StoppableThread import StoppableThread


class Server(StoppableThread):
    def __init__(self, node: Node, routing_table: RoutingTable, lookup_count: int):
        StoppableThread.__init__(self)
        self.node = node
        self.port = node.port
        self.routing_table = routing_table
        self.lookup_count = lookup_count
        self.messages = []

    def run(self):
        with socketmanager() as sock:
            sock.bind(('', self.port))
            sock.listen(100)
            print("Server has started")
            while True:
                if self.stopped():
                    return
                conn, sender_address = sock.accept()
                print(f"Client connected, ip {sender_address}\r\n")
                data = conn.recv(1024).decode(encoding='utf-8')
                sender_credentials, cmd, payload = data.split(' ')
                print(f"got {cmd} from {sender_credentials}, content: {payload}")
                sender_id, sender_port = sender_credentials.split(':')
                response = self.handle_command(sender_id, sender_address[0], int(sender_port), cmd, payload)
                conn.send(response.encode(encoding="utf-8"))
                conn.close()

    def handle_command(self, sender_id: str, sender_ip, sender_port, cmd, payload: str):
        sender_node = Node(sender_id, sender_ip, sender_port)
        if cmd == "FIND_NODE":
            self.routing_table.add_node(sender_node)
            closest_nodes = self.routing_table.get_closest_nodes(payload, self.lookup_count)
            return json.dumps(closest_nodes, default=lambda x: x.__dict__)

        if cmd == "STORE":
            self.routing_table.add_node(sender_node)
            self.messages.append(Message(sender_node, payload))
            return "ok"

        if cmd == "PING":
            return "PONG"
