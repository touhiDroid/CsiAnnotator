import json

from src.helpers import format_bytes


class EspDevice(object):
    def __init__(self, name, channel, tx_rate, file_size, live_data=None):
        super().__init__()
        self.name = name
        self.channel = channel
        self.tx_rate = tx_rate
        self.file_size = file_size
        self.live_data = live_data

    @staticmethod
    def from_json(json_str):
        j = json.loads(json_str)
        name = j['device_name']
        ch = j['wifi_channel']
        tss = j['data_rate'].split('\n')
        tx_rate = int(tss[-2].split(',')[1])
        file_size = j['files_size']
        live_data = j['live_data'] if 'live_data' in j else None
        return EspDevice(name, ch, tx_rate, file_size, live_data)

    def get_str(self):
        return (f"{self.name[self.name.rindex('/') + 1:]}, Ch-{self.channel}, "
                f"{format_bytes(self.file_size)}, {self.tx_rate}Hz")

    @staticmethod
    def get_list_to_str(devices):
        i = 1
        _str = ""
        for d in devices:
            _str += f"{i}. {d.get_str()}\n"
            i += 1
        return _str
