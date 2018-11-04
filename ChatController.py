from _sha1 import sha1
from collections import deque
from flask import Blueprint, render_template, request


def create_chat_controller(command_queue: deque, contacts: list):

    chat_controller = Blueprint('chat_controller', __name__)

    @chat_controller.route("/")
    def index():
        return render_template("index.html", contacts=contacts)

    @chat_controller.route("/send", methods=['POST'])
    def send():
        message = request.form['message']
        username = request.form['username']
        user_hash = _get_hash(username)
        command_queue.append(f"{user_hash}:{message}")
        return render_template("index.html", contacts=contacts)

    @chat_controller.route("/dialog/<username>")
    def dialog(username: str):
        return render_template("index.html", contacts=contacts, username=username, user_hash=_get_hash(username))

    def _get_hash(username: str):
        return sha1(bytes(username, encoding='utf-8')).hexdigest()

    return chat_controller