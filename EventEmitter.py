import base64
from collections import deque
from threading import Thread
from flask_socketio import SocketIO


class EventEmitter(Thread):
    def __init__(self, message_queue: deque, io: SocketIO):
        Thread.__init__(self)
        self.msg_queue = message_queue
        self.io = io

    def run(self):
        while True:
            if len(self.msg_queue) is not 0:
                new_message = self.msg_queue.pop().content
                self.io.emit('message', {'msg': base64.b64decode(new_message).decode("utf-8")})
