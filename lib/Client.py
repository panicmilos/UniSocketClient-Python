class Client(object):
    def __init__(self, name: str):
        super().__init__()
        self._name = name

    def connect(self, host: str, port: int):
        pass

    def send_to_client(self, session_name: str, data):
        pass

    def send_to_clients(self, session_names: str, data):
        pass

    def broadcast(self, data):
        pass

    def disconnect(self):
        pass