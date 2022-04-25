from configparser import ConfigParser
from os.path import expanduser, join, exists
from pprint import pprint
import requests
import time
import json

MESSAGE_TYPE_FLUSH = 3

FAASM_INI_FILE = join(expanduser("~"), ".config", "faasm.ini")


def get_faasm_ini_value(section, key):
    if not exists(FAASM_INI_FILE):
        print("Expected to find faasm config at {}".format(FAASM_INI_FILE))
        raise RuntimeError("Did not find faasm config")

    config = ConfigParser()
    config.read(FAASM_INI_FILE)
    return config[section].get(key, "")


def get_faasm_upload_host_port():
    host = get_faasm_ini_value("Faasm", "upload_host")
    port = get_faasm_ini_value("Faasm", "upload_port")

    print("Using faasm upload {}:{}".format(host, port))

    return host, port


def get_faasm_invoke_host_port():
    host = get_faasm_ini_value("Faasm", "invoke_host")
    port = get_faasm_ini_value("Faasm", "invoke_port")

    print("Using faasm invoke {}:{}".format(host, port))

    return host, port


def get_faasm_worker_pods():
    pods = get_faasm_ini_value("Faasm", "worker_names")
    pods = [p.strip() for p in pods.split(",") if p.strip()]

    print("Using faasm worker pods: {}".format(pods))
    return pods


def get_knative_headers():
    knative_host = get_faasm_ini_value("Faasm", "knative_host")
    return {"Host": knative_host}


def invoke_and_await(user, func, msg, interval=2):
    host, port = get_faasm_invoke_host_port()
    headers = get_knative_headers()
    url = "http://{}:{}".format(host, port)

    # Invoke
    print("Posting to {}".format(url))
    pprint(msg)

    response = requests.post(url, json=msg, headers=headers)

    if response.status_code != 200:
        print(
            "Initial request failed: {}:\n{}".format(
                response.status_code, response.text
            )
        )
    print("Response: {}".format(response.text))

    msg_id = int(response.text.strip())
    print("Polling message {}".format(msg_id))

    while True:
        time.sleep(interval)

        status_msg = {
            "user": user,
            "function": func,
            "status": True,
            "id": msg_id,
        }
        response = requests.post(
            url,
            json=status_msg,
            headers=headers,
        )

        print(response.text)
        if response.text.startswith("RUNNING"):
            continue
        elif response.text.startswith("FAILED"):
            raise RuntimeError("Call failed")
        elif not response.text:
            raise RuntimeError("Empty status response")

        # Try to parse to json
        result_data = json.loads(response.text)

        # Get Faasm reported time
        start_ms = int(result_data["timestamp"])
        end_ms = int(result_data["finished"])

        actual_seconds = (end_ms - start_ms) / 1000.0

        output_data = result_data["output_data"]
        return actual_seconds, output_data


def faasm_flush():
    host, port = get_faasm_invoke_host_port()
    knative_headers = get_knative_headers()
    url = "http://{}:{}".format(host, port)

    msg = {"type": MESSAGE_TYPE_FLUSH}
    response = requests.post(
        url, json=msg, headers=knative_headers, timeout=None
    )
    if response.status_code != 200:
        print(
            "Flush request failed: {}:\n{}".format(
                response.status_code, response.text
            )
        )
    print("Waiting for flush to propagate...")
    time.sleep(5)
    print("Done waiting")
