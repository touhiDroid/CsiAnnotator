from enum import Enum


class ServerStatus(Enum):
    NONE = 0
    OK = 1
    GOING = 2
    GONE = 3


class AppCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.variable = "Hello"
        return cls._instance

    def __init__(self):
        self.missed_server_calls = 0
        self.server_stat = None
        self.esp_devices = []
        self.server_status = None
