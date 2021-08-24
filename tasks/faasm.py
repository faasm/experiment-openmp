from configparser import ConfigParser
from os.path import expanduser, join, exists


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
    ip = get_faasm_ini_value("Faasm", "hoststats_host")
    print("Using hoststats proxy {}".format(ip))
    return ip


def get_faasm_worker_pods():
    ips = get_faasm_ini_value("Faasm", "worker_hoststats_ips")
    print("Using faasm workers {}".format(ips))
    return ips
