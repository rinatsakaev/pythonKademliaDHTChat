from User import User


class Main:
    def __init__(self):
        self.user = None
        self.login = None

    def main(self):
        self.login = "rinat"
        self.user = User(self.login, "current_ip")
        self.register_user()

    def register_user(self):
        self.user.node.discover_node_ip(self.user.node.id, None)


if __name__ == "__main__":
    maincls = Main()
    maincls.main()
