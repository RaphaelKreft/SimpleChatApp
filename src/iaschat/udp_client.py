#!/usr/bin/env python3

"""
udp_client: Allows to chat with one other udp client. It first connects to a udp_server and register itself
            and requests the connection information from a peer. When the server response with valid connection-info
            then you can start chatting.
"""

import argparse
import socket
import select
import sys

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
CORRESPONDENT = None


def parse_args():
    parser = argparse.ArgumentParser(description="Enter IP and Port to Connect to")
    parser.add_argument('-ip', type=str, default="127.0.0.1", required=True)
    parser.add_argument('-p', '-port', type=int, default=2020, required=True)
    parser.add_argument('-tonick', type=str, required=True)
    parser.add_argument('-mynick', type=str, required=True)
    return parser.parse_args()


def send_message(msg):
    message_queue.put("{}:{}".format(ClientProtocol.MSG.value, msg).encode())
    outputs.append(sock)


def request_name(name):
    message_queue.put("{}:{}".format(ServerProtocol.REGISTER.value, name).encode())
    outputs.append(sock)


def request_peer_info(nickname):
    message_queue.put("{}:{}".format(ServerProtocol.REQUEST.value, nickname).encode())
    outputs.append(sock)


def establish_connection(cor):
    if cor:
        ip, port = cor.split("_")
        global CORRESPONDENT
        CORRESPONDENT = (ip, int(port))
        print_debug("Set Correspondent to {}".format(CORRESPONDENT))
        message_queue.put("{}:---{}--- wants to communicate!".format(ClientProtocol.MSG.value, args.mynick).encode())
        outputs.append(sock)
    else:
        exit("Could not find nickname you requested on Server!")


if __name__ == "__main__":
    args = parse_args()

    if not port_valid(args.p):
        exit("Port {} is not in range!".format(args.p))

    inputs = [sys.stdin]
    outputs = []
    message_queue = queue.Queue()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", int(args.p) + 1))
    inputs.append(sock)

    # First set correspondent to the server
    CORRESPONDENT = (args.ip, args.p)

    # Send requests to server
    print_debug("Send requests to Server...")
    request_name(args.mynick)
    request_peer_info(args.tonick)

    while inputs:
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)
        for r in readable:
            if r is sock:
                data, addr = r.recvfrom(BUFFER_SIZE)
                print_debug("Received data from {}".format(addr))
                if data:
                    toHandle = data.decode().split(":")
                    if toHandle[0] == ClientProtocol.LOGINDATA.value:
                        print("Your nickname on the server is: {}".format(toHandle[1]))
                        args.mynick = toHandle[1]
                    elif toHandle[0] == ClientProtocol.PEERINFO.value:
                        establish_connection(toHandle[1])
                    elif toHandle[0] == ClientProtocol.MSG.value:
                        print("msg: {}".format(toHandle[1]))
                    else:
                        print_debug("Invalid Command received: {}".format(toHandle[0]))
            elif r is sys.stdin:
                send_message(sys.stdin.readline())
                if sock not in outputs:
                    outputs.append(sock)

        for w in writeable:
            if message_queue.empty():
                outputs.remove(w)
            else:
                print_debug("Sending to {}".format(CORRESPONDENT))
                w.sendto(message_queue.get_nowait(), CORRESPONDENT)

        for e in exceptional:
            exit("Exception!")
            inputs.remove(e)
            if e in outputs:
                outputs.remove(e)
            e.close()
