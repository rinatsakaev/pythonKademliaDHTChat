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
        s.shutdown(socket.SHUT_RDWR)
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
