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
NICKNAME = None
CORRESPONDENT = None


def parse_args():
    parser = argparse.ArgumentParser(description="Enter IP and Port to Connect to")
    parser.add_argument('-ip', type=str, required=True, help="Ip of udp_server instance")
    parser.add_argument('-p', '-port', type=int, required=True, help="Port of udp_server instance")
    parser.add_argument('-mp', '-myport', type=int, required=True, help="Port to bind own socket to")
    return parser.parse_args()


def send_message(msg):
    message_queue.put("{}:{}".format(ClientProtocol.MSG.value, msg))
    outputs.append(sock)


def request_name(name):
    message_queue.put("{}:{}".format(ServerProtocol.REGISTER.value, name))
    outputs.append(sock)


def request_peer_info(nickname):
    message_queue.put("{}:{}".format(ServerProtocol.REQUEST.value, nickname))
    outputs.append(sock)


def establish_connection(cor):
    global CORRESPONDENT
    if cor:
        ip, port = cor.split("_")
        CORRESPONDENT = (ip, int(port))
        print_debug("Set Correspondent to {}".format(CORRESPONDENT))
        message_queue.put("{}:{}".format(ClientProtocol.PTPREQUEST.value, NICKNAME))
        outputs.append(sock)
    else:
        print("Could not find nickname you requested on Server!, correspondent is still {}".format(CORRESPONDENT))


if __name__ == "__main__":
    args = parse_args()

    if not port_valid(args.p):
        exit("Port {} is not in range!".format(args.p))

    inputs = [sys.stdin]
    outputs = []
    message_queue = queue.Queue()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", int(args.mp)))
    inputs.append(sock)

    # First set correspondent to the server
    SERVER = (args.ip, args.p)

    while inputs:
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)
        for r in readable:
            if r is sock:
                data, addr = r.recvfrom(BUFFER_SIZE)
                print_debug("Received data from {}".format(addr))
                if data:
                    toHandle = data.decode().split(":")
                    if toHandle[0] == ClientProtocol.LOGINDATA.value:
                        if toHandle[1]:
                            print("Your nickname on the server is: {}".format(toHandle[1]))
                            NICKNAME = toHandle[1]
                        else:
                            print("Your Requested Nickname was already occupied on server!")
                    elif toHandle[0] == ClientProtocol.PEERINFO.value:
                        establish_connection(toHandle[1])
                    elif toHandle[0] == ClientProtocol.MSG.value:
                        print("msg: {}".format(toHandle[1]))
                    elif toHandle[0] == ClientProtocol.PTPREQUEST.value:
                        print("Direct comm-request from {}".format(toHandle[1]))
                        CORRESPONDENT = addr
                        print("Correspondent set to {}".format(addr))
                    else:
                        print_debug("Invalid Command received: {}".format(toHandle[0]))
            elif r is sys.stdin:
                cmd = sys.stdin.readline()
                if cmd.startswith("cmd:register"):
                    request_name(cmd.split(" ")[1])
                elif cmd.startswith("cmd:request"):
                    request_peer_info(cmd.split(" ")[1])
                else:
                    send_message(cmd)
                if sock not in outputs:
                    outputs.append(sock)

        for w in writeable:
            if message_queue.empty():
                outputs.remove(w)
            else:
                msg = message_queue.get_nowait()
                if msg.startswith(ServerProtocol.REQUEST.value) or msg.startswith(ServerProtocol.REGISTER.value):
                    print_debug("Sending to {}".format(SERVER))
                    w.sendto(msg.encode(), SERVER)
                else:
                    print_debug("Sending to {}".format(CORRESPONDENT))
                    w.sendto(msg.encode(), CORRESPONDENT)

        for e in exceptional:
            exit("Exception!")
            inputs.remove(e)
            if e in outputs:
                outputs.remove(e)
            e.close()
