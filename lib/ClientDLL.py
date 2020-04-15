import json
from ctypes import *
import os

CB_F_TYPE = CFUNCTYPE(c_int, c_char_p)

dll_path = os.path.abspath(__file__)
dll_path = os.path.realpath(dll_path)
dll_path = os.path.dirname(dll_path)

os.environ['PATH'] = dll_path + ";" + os.environ['PATH']


class ClientDLL(object):
    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._event_handlers = {}
        self._data_callback = CB_F_TYPE(self._data_read_callback)
        self._info_callback = CB_F_TYPE(self._info_read_callback)
        self._error_callback = CB_F_TYPE(self._error_read_callback)
        self._ClientDLL = cdll.LoadLibrary("UniSocketClient.dll")
        self._client = self._ClientDLL.client(bytes(self._name, 'utf-8')
                                              , self._data_callback
                                              , self._info_callback
                                              , self._error_callback)
        self._receivers = ""
        self._is_broadcast = False
        self._num_of_receivers = 0

    def connect(self, host: str, port: str):
        self._ClientDLL.connect_to_server(self._client, bytes(host, 'utf-8'), bytes(port, 'utf-8'))

    def disconnect(self):
        self._ClientDLL.disconnect(self._client)

    def on(self, event_name, handler):
        self._event_handlers[event_name] = handler

    def to(self, client_name: str):
        self._num_of_receivers += 1
        self._receivers += client_name if self._receivers == "" else "," + client_name
        return self

    def to_clients(self, client_names: list):
        self._num_of_receivers += len(client_names)
        for client_name in client_names:
            self._receivers += client_name if self._receivers == "" else "," + client_name
        return self

    def broadcast(self):
        self._is_broadcast = True
        return self

    def emit(self, event_name: str, data):
        data_dict = {"event_name": event_name, "data": data}
        data_json_string = json.dumps(data_dict)

        if self._is_broadcast:
            self._broadcast(data_json_string)

        if self._num_of_receivers == 1:
            self._send_to_client(data_json_string)

        elif self._num_of_receivers == 0:
            self._custom_event(data_json_string)

        else:
            self._send_to_clients(data_json_string)

        self._reset_receivers()

    def _send_to_client(self, data: str):
        self._ClientDLL.send_to_client(self._client, bytes(self._receivers, 'utf-8'), bytes(data, 'utf-8'))

    def _send_to_clients(self, data: str):
        self._ClientDLL.send_to_clients(self._client, bytes(self._receivers, 'utf-8'), bytes(data, 'utf-8'))

    def _broadcast(self, data):
        self._ClientDLL.broadcast(self._client, bytes(data, 'utf-8'))

    def _custom_event(self, data):
        self._ClientDLL.custom_event(self._client, bytes(data, 'utf-8'))

    def _reset_receivers(self):
        self._receivers = ""
        self._is_broadcast = False
        self._num_of_receivers = 0

    def _data_read_callback(self, data: str):
        data_string = data.decode("utf-8")
        try:
            data_dict = json.loads(data_string)
        except Exception as e:
            print("Invalid JSON format in: " + data_string)
            print("Exception", e)
            return -1
        self._handle_data_event(data_dict)
        return 0

    def _handle_data_event(self, data_dict):
        event_name = data_dict["event_name"]
        data = data_dict["data"]
        handler = self._event_handlers[event_name]
        if handler:
            handler(data)

    def _error_read_callback(self, message: str):
        error_event_handler = self._event_handlers["error"]
        if error_event_handler:
            error_event_handler(message)
        else:
            print(f"Unhandled error response from server: \n{message}")
        return 0

    def _info_read_callback(self, message: str):
        info_event_handler = self._event_handlers["info"]
        if info_event_handler:
            info_event_handler(message)
        else:
            print(f"Info message from server: \n{message}")
        return 0
