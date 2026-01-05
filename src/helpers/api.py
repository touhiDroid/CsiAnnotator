import json
import os
import traceback
from sys import stderr

import numpy as np
import requests
import zmq
from dotenv import load_dotenv, set_key
from requests.structures import CaseInsensitiveDict
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
        server_address = get_server_address()
        print(f"Server address: {server_address}")  # Log the server address
        resp = requests.post(f'{server_address}/reset', params=params)
        print_response(resp)
    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError) as err:
        resp = None
        stderr.write(f"Connection error: {str(err)}\n")
    except Exception as err:
        resp = None
        stderr.write(f"Unexpected error: {str(err)}\n")
        stderr.write(traceback.format_exc())
    return resp


# def reset_for_new_session(participant_name):
#     params = (('participant', participant_name),)
#     try:
#         resp = requests.post(f'{get_server_address()}/reset', params=params)
#         print_response(resp)
#     except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
#         resp = None
#         stderr.write(str(err) + "\n")
#         pass
#     return resp


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


def get_device_data(device_name, duration=60):
    params = (('device_name', device_name), ('duration', duration))
    try:
        resp = requests.get(f'{get_server_address()}/data/device', params=params)
        if resp is not None and resp.status_code == 200:
            return EspDevice.from_json(resp.content)
        else:
            stderr.write(str(resp) + "\n")
            return None
    except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
        resp = None
        stderr.write(str(err) + "\n")
    return resp


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
    try:
        if resp is not None and resp.status_code == 200:
            if class_name is not None:
                print(f"Posted NEW action `{class_name}` to perform now ...")
            else:
                print(f"API Response: {resp.text}")
        else:
            status_code = str(resp.status_code if resp is not None else "NULL")
            text = str(resp.text if resp is not None else "NULL")
            stderr.write(f"Bad Service!\nResponse Code: {status_code}\nResponse: {text}\n")
    except Exception as e:
        stderr.write(f"Error in print_response: {str(e)}\n")
        stderr.write(traceback.format_exc())


def print_response_old(resp, class_name=None):
    if resp is not None and resp.status_code == 200:
        if class_name is not None:
            print("Posted NEW action `{:s}` to perform now ...".format(class_name))
        else:
            print("API Response: ", resp.text)
    else:
        stderr.write("Bad Service!\nResponse Code: "
                     + str(resp.status_code if resp is not None else "NULL")
                     + "\nResponse: " + str(resp.text if resp is not None else "NULL\n"))


def post_to_discord(post_data):
    try:
        print("Posting: ", post_data, '\n')

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        data = {'content': post_data}

        resp = requests.post(os.environ["DISCORD_WEBHOOK_URL"], headers=headers, data=json.dumps(data))
        print(resp.text)
    except Exception as err:
        resp = None
        stderr.write(str(err) + "\n")
        pass
    return resp


def get_prediction_server_socket():
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    host = get_server_host()
    socket.connect(f"tcp://{host}:5557")
    return socket


def request_prediction(model_key, csi_window):
    """Send CSI amplitude window + model key to WiPT-ML ZeroMQ server"""
    payload = {
        "model_key": model_key,  # e.g. "vertical", "horizontal",
        # "wipt_ensemble", "wipt_h", "wipt_v", "wipt_lr", "wipt_rl",
        # "hand_ch1", "hand_ch3", "hand_ch5", "hand_ch7"
        "data": np.array(csi_window)  # array of Numpy 2D arrays with shape = (150, 32)
        # each item = a single WiFi link data making ensemble prediction possible
    }
    socket = get_prediction_server_socket()
    socket.send_pyobj(payload)
    result = socket.recv_pyobj()
    return result
