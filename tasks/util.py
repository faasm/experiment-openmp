from os.path import dirname, realpath, expanduser, join

HOME_DIR = expanduser("~")
PROJ_ROOT = dirname(dirname(realpath(__file__)))
COVID_DIR = join(PROJ_ROOT, "third-party", "covid-sim")
