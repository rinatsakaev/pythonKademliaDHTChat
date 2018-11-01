import threading
from collections import deque

from ChatController import create_chat_controller
from flask import Flask
from flask_socketio import SocketIO, emit, send

from EventEmitter import EventEmitter


class FlaskThread(threading.Thread):
    def __init__(self, command_queue: deque, messages_queue: deque):
        threading.Thread.__init__(self)
        self.app = Flask(__name__)
        self.messages_queue = messages_queue
        self.app.register_blueprint(create_chat_controller(command_queue))
        self.socketIO = SocketIO(self.app)

    def run(self):
        EventEmitter(self.messages_queue, self.socketIO).start()
        self.socketIO.run(self.app, debug=True, use_reloader=False)