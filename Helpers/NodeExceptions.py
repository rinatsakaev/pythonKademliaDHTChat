class NodeNotFoundException(Exception):
    def __init__(self, message):
        super(NodeNotFoundException).__init__(message)
