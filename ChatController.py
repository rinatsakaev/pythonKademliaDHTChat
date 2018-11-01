from collections import deque
from flask import Blueprint, render_template, request


def create_chat_controller(command_queue: deque):

    chat_controller = Blueprint('chat_controller', __name__)

    @chat_controller.route("/")
    def index():
        return render_template("index.html")

    @chat_controller.route("/send", methods=['POST'])
    def send():
        message = request.form['message']
        recipient_id = request.form['recipient_id']
        command_queue.append(f"{recipient_id}:{message}")
        return render_template("index.html")

    return chat_controller
