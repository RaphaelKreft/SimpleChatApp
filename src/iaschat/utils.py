DEBUG = 1


def port_valid(port):
    return 65536 > port > 1024


def print_debug(text):
    if DEBUG == 1:
        print(">> {}".format(text))


def valid_multicast_ip(ip):
    return