from configparser import ConfigParser
from subprocess import run, PIPE
from os.path import expanduser, join, exists
import json

from tasks.util import PROJ_ROOT

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


def get_faasm_hoststats_proxy_ip():
    res = run(
        "kubectl -n faasm get service hoststats-proxy -o json",
        stdout=PIPE,
        stderr=PIPE,
        cwd=PROJ_ROOT,
        shell=True,
        check=True,
    )

    data = json.loads(res.stdout.decode("utf-8"))
    ip = data["spec"]["clusterIP"]
    print("Got hoststats proxy IP {}".format(ip))
    return ip


def get_faasm_worker_pods():
    kubecmd = [
        "kubectl",
        "-n faasm",
        "get pods",
        "-l serving.knative.dev/service=faasm-worker",
        "-o wide",
    ]

    kubecmd = " ".join(kubecmd)
    print(kubecmd)
    res = run(
        kubecmd,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
        check=True,
    )

    cmd_out = res.stdout.decode("utf-8")

    # Split output into list of strings
    lines = cmd_out.split("\n")[1:]
    lines = [l.strip() for l in lines if l.strip()]

    pod_names = list()
    pod_ips = list()
    for line in lines:
        line_parts = line.split(" ")
        line_parts = [p.strip() for p in line_parts if p.strip()]

        pod_names.append(line_parts[0])
        pod_ips.append(line_parts[5])

    return pod_names, pod_ips
