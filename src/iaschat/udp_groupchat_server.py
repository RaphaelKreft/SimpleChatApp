#!/usr/bin/env python3

"""
udp_server.py:
"""

import argparse
import socket
import select
import random

try:
    import queue
except ImportError:
    import Queue as queue

from server_protocol import ServerProtocol
from client_protocol import ClientProtocol
from utils import *


__author__ = "Tim Bachmann, Raphael Kreft"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Raphael Kreft"
__email__ = "r.kreft@unibas.ch"
__status__ = "Production"


BUFFER_SIZE = 1024
GROUPS = {}


def parse_args():
    parser = argparse.ArgumentParser(description="Enter IP and Port to Connect to")
    parser.add_argument('-p', '-port', type=int, default=2020, required=True)
    return parser.parse_args()


def register_client(name):
    print_debug("Connection {} wants to register with name {}".format(addr, name))
    # Check if own nickname already registered and matching incoming address
    if not (name.lower() in name_to_addr.keys() and name_to_addr.get(name.lower()) is addr):
        while name.lower() in name_to_addr.keys():
            name += random.choice(['a', 'b', 'c', 'd'])
        name_to_addr[name] = addr
    print_debug("{} got registered with name {}".format(addr, name))
    message_queue.put((addr, "{}:{}".format(ClientProtocol.LOGINDATA.value, name)))
    outputs.append(sock)


def get_group_info(to_lookup):
    print_debug("Connection {} requested group info for {}".format(addr, to_lookup))
    if to_lookup in GROUPS.keys():
        packaged_addr = "{}_{}".format(GROUPS.get(to_lookup)[0], GROUPS.get(to_lookup)[1])
        message_queue.put((addr, "{}:{}".format(ClientProtocol.GRPINFO.value, packaged_addr)))
    else:
        message_queue.put((addr, "{}:".format(ClientProtocol.GRPINFO.value)))
    outputs.append(sock)


def get_group_table():
    print_debug("Group Table requested from {}".format(addr))
    message_queue.put((addr, "{}:".format(ClientProtocol.GRPTABLE.value) + "_".join(GROUPS.keys())))
    outputs.append(sock)


def create_group(new_group):
    name, ip, port = new_group.split("_")
    if name in GROUPS.keys():
        message_queue.put((addr, "{}:".format(ClientProtocol.GRPCREATED.value)))
    else:
        GROUPS[name] = (ip, port)
        message_queue.put((addr, "{}:1".format(ClientProtocol.GRPCREATED.value)))
    outputs.append(sock)


if __name__ == "__main__":
    args = parse_args()

    if not port_valid(args.p):
        exit("Port {} is not in range!".format(args.p))
    else:
        print("Port valid, start server...")
    inputs = []
    outputs = []
    name_to_addr = {}
    # This queue saves a tuple ((ip, port), data)
    message_queue = queue.Queue()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", int(args.p)))
    inputs.append(sock)

    while inputs:
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)
        for r in readable:
            data, addr = r.recvfrom(BUFFER_SIZE)
            print_debug("Received data from {}".format(addr))
            if data:
                cmd, rest = data.decode().split(":")
                if cmd == ServerProtocol.GROUPS.value:
                    get_group_table()
                elif cmd == ServerProtocol.REGISTER.value:
                    register_client(rest)
                elif cmd == ServerProtocol.CRGROUP.value:
                    create_group(rest)
                elif cmd == ServerProtocol.GACCESS.value:
                    get_group_info(rest)
                else:
                    print_debug("Got Unknown Command {} from {}".format(cmd, addr))
            else:
                inputs.remove(r)
                r.close()

        for w in writeable:
            if not message_queue.empty():
                addr, to_send = message_queue.get_nowait()
                print_debug("Try to send to {}".format(addr))
                w.sendto(to_send.encode(), addr)
            else:
                outputs.remove(w)

        for e in exceptional:
            print("Exception!")
            inputs.remove(e)
            e.close()
