class Message:
    def __init__(self, sender_node, content, public_node=None):
        self.sender_node = sender_node
        self.content = content
        self.public_node = public_node
