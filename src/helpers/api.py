import json
import os
from sys import stderr

import requests
from dotenv import load_dotenv, set_key
from urllib3.exceptions import NewConnectionError, MaxRetryError

from src.models.EspDevice import EspDevice

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
        print_response(resp)
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
        resp = requests.get(f'{get_server_address()}/server-stats', params=None)
        if resp is not None and resp.status_code == 200:
            j = json.loads(resp.content)
            return (j['data_directory'],
                    j['storage']['used'],
                    j['storage']['total'],
                    j['devices'])
    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
        resp = None
        stderr.write(str(err) + "\n")
        pass
    return None


def get_esp_device_details(device_name):
    params = (('device_name', device_name),)
    try:
        resp = requests.get(f'{get_server_address()}/device-metrics', params=params)
        if resp is not None and resp.status_code == 200:
            return EspDevice.from_json(resp.content)
        else:
            stderr.write(str(resp) + "\n")
            return None
    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
        resp = None
        stderr.write(str(err) + "\n")
    return resp


def print_response(resp, class_name=None):
    if resp is not None and resp.status_code == 200:
        if class_name is not None:
            print("Posted NEW action `{:s}` to perform now ...".format(class_name))
        else:
            print("API Response: ", resp.text)
    else:
        stderr.write("Bad Service!\nResponse Code: "
                     + str(resp.status_code if resp is not None else "NULL")
                     + "\nResponse: " + str(resp.text if resp is not None else "NULL\n"))
