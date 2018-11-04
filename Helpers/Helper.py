import base64
import socket
from contextlib import contextmanager

from Models.Node import Node


@contextmanager
def socketmanager(*args, **kw):
    s = socket.socket(*args, **kw)
    try:
        yield s
    except ConnectionError:
        print(f"Can't connect to node ^")
    finally:
        s.close()


def xor(a: str, b: str):
    raw = bytes(ord(x) ^ ord(y) for x, y in zip(a, b))
    return int.from_bytes(raw, byteorder="big")


def ping_node(node: Node):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((node.ip, node.port))
        s.send(bytes(f"{node.id}:{node.port} PING 0", encoding="utf-8"))
        response = s.recv(1024).decode(encoding="utf-8")
        if response == "PONG":
            return True
    except ConnectionError:
        return False
    finally:
        s.close()


def send_command(from_node: Node, to_node: Node, command: str, data: str):
    with socketmanager(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to {to_node.ip}:{to_node.port} ({command})")
        s.connect((to_node.ip, to_node.port))
        s.send(bytes(f"{from_node.id}:{from_node.port} {command} {data}",
                     encoding="utf-8"))
