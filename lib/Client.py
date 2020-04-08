import json
from ctypes import *
import os

CB_F_TYPE = CFUNCTYPE(c_int, c_char_p)

class Client(object):
    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._event_handlers = {}
        self._on_read_data = CB_F_TYPE(self._read_callback)
        self._ClientDLL = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../dll/UniSocketClientPython.dll"))
        self._client = self._ClientDLL.client(bytes(self._name, 'utf-8'), self._on_read_data)
        self._receivers = ""
        self._num_of_receivers = 0

    def connect(self, host: str, port: int):
        self._ClientDLL.connect_to_server(self._client, bytes(host, 'utf-8'), bytes(port, 'utf-8'))

    def disconnect(self):
        self._ClientDLL.disconnect(self._client)

    def on(self, event_name, handler):
        self._event_handlers[event_name] = handler

    def to(self, client_name: str):
        self._num_of_receivers += 1
        self._receivers += client_name if self._receivers == "" else "," + client_name
        return self

    def emit(self, event_name: str, data):
        data_dict = {}
        data_dict["event_name"] = event_name
        data_dict["data"] = data
        data_json_string = json.dumps(data_dict)

        if self._num_of_receivers == 1:
            self._send_to_client(data_json_string)

        elif self._num_of_receivers == 0:
            self._broadcast(data_json_string)

        else:
            self._send_to_clients(data_json_string)

        self._reset_receivers()

    def _send_to_client(self, data: str):
        self._ClientDLL.send_to_client(self._client, bytes(self._receivers, 'utf-8'), bytes(data, 'utf-8'))

    def _send_to_clients(self, data: str):
        self._ClientDLL.send_to_clients(self._client, bytes(self._receivers, 'utf-8'), bytes(data, 'utf-8'))

    def _broadcast(self, data):
        self._ClientDLL.broadcast(self._client, bytes(data, 'utf-8'))

    def _reset_receivers(self):
        self._receivers = ""
        self._num_of_receivers = 0

    def _read_callback(self, data: str):
        data_string = data.decode("utf-8")
        try:
            data_dict = json.loads(data_string)
            event_name = data_dict.event_name
            handler = self._event_handlers[event_name]
            handler(data_dict)
        except Exception:
            print("Invalid JSON format in: " + data_string)
        return 0
