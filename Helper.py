import socket
from contextlib import contextmanager

@contextmanager
def socketmanager(*args, **kw):
    s = socket.socket(*args, **kw)
    try:
        yield s
    except ConnectionError:
        print(f"Something is wrong with {args[0]}")
    finally:
        s.close()


def xor(a: str, b: str):
    raw = bytes(ord(x) ^ ord(y) for x, y in zip(a, b))
    return int.from_bytes(raw, byteorder="big")
