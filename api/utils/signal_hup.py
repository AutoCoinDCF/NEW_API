import signal
import ConfigParser


def get_config():
    conf = ConfigParser.ConfigParser()
    conf.read("config.cfg")
    name = conf.get("test", "name")
    print(name)


def update_config(signum, frame):
    print("update config")
    get_config()


def ctrl_c(signum, frame):
    print("input ctrl c")
    exit(1)


# 捕获HUP
signal.signal(signal.SIGHUP, update_config)
# 捕获ctrl+c
signal.signal(signal.SIGINT, ctrl_c)

print("test signal")
get_config()

while True:
    pass
