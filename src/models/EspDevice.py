class EspDevice(object):
    def __init__(self, path, channel, tx_rate, file_size):
        super().__init__()
        self.path = path
        self.channel = channel
        self.tx_rate = tx_rate
        self.file_size = file_size
