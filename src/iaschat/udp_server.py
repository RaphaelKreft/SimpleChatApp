#!/usr/bin/env python3

"""
udp_server.py:
"""

import argparse
import socket
import select
import sys
import random

__author__ = "Tim Bachmann, Raphael Kreft"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Raphael Kreft"
__email__ = "r.kreft@unibas.ch"
__status__ = "Production"

BUFFERSIZE = 1024


def parse_args():
    parser = argparse.ArgumentParser(description="Enter IP and Port to Connect to")
    parser.add_argument('-p', '-port', type=int, default=2020, required=True)
    return parser.parse_args()


def port_valid(port):
    return 65536 > port > 1024


if __name__ == "__main__":
    args = parse_args()

    if not port_valid(args.p):
        exit("Port {} is not in range!".format(args.p))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)

    inputs = [sys.stdin]
    outputs = []
    name_to_addr = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", int(args.p)))
    inputs.append(sock)

    while inputs:
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)
        for r in readable:
            data, addr = r.recvfrom(BUFFERSIZE)
            if data:
                own_name, peer_name = data.split(":")
                # Check if own nickname already registered and matching incoming address
                if not (own_name.lower() in name_to_addr.keys() and name_to_addr.get(own_name.lower()) is addr):
                    while own_name.lower() in name_to_addr.keys():
                        own_name += random.choice(['a', 'b', 'c', 'd'])
                    name_to_addr.update((own_name, addr))

                # Check if peer_address known
                if peer_name.lower() in name_to_addr.keys():
                    peer_name = name_to_addr.get(peer_name)
                else:
                    peer_name = "FALSE"
                # create queue and queue response
                sock.sendto("{}:{}".format(own_name, peer_name).encode(), addr)
            else:
                inputs.remove(r)
                r.close()

        for e in exceptional:
            print("Exception!")
            inputs.remove(e)
            e.close()
