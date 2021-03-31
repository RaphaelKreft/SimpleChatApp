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
    message_queue.put((addr, "{}:{}".format(ClientProtocol.LOGINDATA.value, name).encode()))
    outputs.append(sock)


def get_user_info(to_lookup):
    print_debug("Connection {} requested peerinfo for {}".format(addr, to_lookup))
    if to_lookup in name_to_addr.keys():
        packaged_addr = "{}_{}".format(name_to_addr.get(to_lookup)[0], name_to_addr.get(to_lookup)[1])
        message_queue.put((addr, "{}:{}".format(ClientProtocol.PEERINFO.value, packaged_addr).encode()))
    else:
        message_queue.put((addr, "{}:".format(ClientProtocol.PEERINFO.value).encode()))
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
                if cmd == ServerProtocol.REQUEST.value:
                    get_user_info(rest)
                elif cmd == ServerProtocol.REGISTER.value:
                    register_client(rest)
                else:
                    print_debug("Got Unknown Command {} from {}".format(cmd, addr))
            else:
                inputs.remove(r)
                r.close()

        for w in writeable:
            if not message_queue.empty():
                addr, to_send = message_queue.get_nowait()
                print_debug("Try to send to {}".format(addr))
                w.sendto(to_send, addr)
            else:
                outputs.remove(w)

        for e in exceptional:
            print("Exception!")
            inputs.remove(e)
            e.close()
