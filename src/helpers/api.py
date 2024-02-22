import os
from sys import stderr

import requests
from dotenv import load_dotenv
from urllib3.exceptions import NewConnectionError, MaxRetryError

load_dotenv()


def get_server_address():
    host = os.getenv("HOST")
    port = os.getenv("PORT")
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


def print_response(resp, class_name):
    if resp is not None and resp.status_code == 200:
        print("Posted NEW action `{:s}` to perform now ...".format(class_name))
    else:
        stderr.write("Bad Service!\nResponse Code: "
                     + str(resp.status_code if resp is not None else "NULL")
                     + "\nResponse: " + str(resp.text if resp is not None else "NULL\n"))
