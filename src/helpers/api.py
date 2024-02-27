import os
from sys import stderr

import requests
from dotenv import load_dotenv, set_key
from urllib3.exceptions import NewConnectionError, MaxRetryError

load_dotenv()


def get_server_host():
    return os.environ["HOST"]


def update_server_host(new_host):
    set_key('.env', "HOST", new_host)
    os.environ["HOST"] = new_host
    load_dotenv()


def get_server_address():
    host = get_server_host()
    port = os.environ["PORT"]
    # noinspection HttpUrlsUsage
    return f"http://{host}:{port}"


def reset_for_new_session(participant_name):
    params = (('participant', participant_name),)
    try:
        resp = requests.post(f'{get_server_address()}/reset', params=params)
    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
        resp = None
        stderr.write(str(err) + "\n")
        pass
    return resp


def post_next_action_label(class_name):
    params = (('value', class_name),)
    try:
        resp = requests.post(f'{get_server_address()}/annotation', params=params)
    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
        resp = None
        stderr.write(str(err) + "\n")
        pass
    return resp


def get_server_stats():
    try:
        resp = requests.get(f'{get_server_address()}/device-metrics', params=None)
        # Json Format: {
        #             'data_directory': self.config.data_dir,
        #             'navigation': self.config.navigation,
        #             'notes': load_from_file(self.config.data_file_names['notes']),
        #             'is_csi_enabled': get_is_csi_enabled(self.config),
        #             'tty_plugins': self.config.tty_plugins,
        #             'storage': {
        #                 'used': shutil.disk_usage("/").used,
        #                 'total': shutil.disk_usage("/").total,
        #             },
        #             'devices': [d.device_path for d in self.config.devices],
        #             'hostname': socket.gethostname(),
        #         }
        if resp is not None and resp.status_code == 200:
            print(resp)  # TODO Parse data-dir & list of devices
    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
        resp = None
        stderr.write(str(err) + "\n")
        pass
    return resp


def get_esp_device_details(device_name):
    params = (('device_name', device_name),)
    try:
        resp = requests.get(f'{get_server_address()}/device-metrics', params=params)
        # resp JSON format = {
        # 'status': 'OK',
        # 'device_name': device_name,
        # 'file': self.config.data_file_names[device_name],
        # 'application': load_from_file(f'/tmp/application/{device_name}'),
        # 'wifi_channel': load_from_file(f'/tmp/wifi_channel/{device_name}'),
        # 'data_rate': os.popen(f'tail -n 60 /tmp/data_rates/{device_name}').read(),
        # 'files_size': os.path.getsize(self.config.data_file_names[device_name]),
        # 'most_recent_csi': {
        #     'samples': os.popen(f'tail -n 3 {self.config.data_file_names[device_name]}').read(),
        # }
        if resp is not None and resp.status_code == 200:
            print(resp)  # TODO Parse & return device metrics (path, channel, data-rate & file-size)

    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
        resp = None
        stderr.write(str(err) + "\n")
        pass
    return resp


def print_response(resp, class_name):
    if resp is not None and resp.status_code == 200:
        print("Posted NEW action `{:s}` to perform now ...".format(class_name))
    else:
        stderr.write("Bad Service!\nResponse Code: "
                     + str(resp.status_code if resp is not None else "NULL")
                     + "\nResponse: " + str(resp.text if resp is not None else "NULL\n"))
