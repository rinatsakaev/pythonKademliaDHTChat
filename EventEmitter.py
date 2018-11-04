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
                new_message = self.msg_queue.pop()
                public_mark_index = new_message.content.find('>')
                if public_mark_index == -1:
                    self.io.emit('message', {'msg': base64.b64decode(new_message.content).decode("utf-8"),
                                            'sender_id': new_message.sender_node.id})
                else:
                    sender_id = new_message.content[1:public_mark_index]
                    content = new_message.content[public_mark_index+1:]
                    self.io.emit('public_message', {'msg': base64.b64decode(content).decode("utf-8"),
                                             'public_node_id': new_message.sender_node.id,
                                             'sender_id': sender_id})
