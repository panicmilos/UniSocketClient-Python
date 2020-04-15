from lib.ClientDLL import ClientDLL


class Client(object):

    def __init__(self, name):
        super().__init__()
        self._clientDLL = ClientDLL(name)

    def connect(self, host: str, port: str):
        self._clientDLL.connect(host, port)

    def disconnect(self):
        self._clientDLL.disconnect()

    def on(self, event_name, handler):
        self._clientDLL.on(event_name, handler)

    def emit(self, event_name: str, data):
        self._clientDLL.emit(event_name, data)

    def to(self, client_name: str):
        return self._clientDLL.to(client_name)

    def to_clients(self, client_names: list):
        return self._clientDLL.to_clients(client_names)

    def broadcast(self):
        return self._clientDLL.broadcast()
