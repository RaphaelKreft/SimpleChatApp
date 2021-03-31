#!/usr/bin/env python3

"""
udp_client: Allows to chat with one other udp client or groups. It first connects to a udp_server and register itself
            and requests the connection information from a peer or group. When the server response with valid
            connection-info then you can start chatting.
"""

import argparse
import struct
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

MULTICAST_TTL = 1


def parse_args():
    parser = argparse.ArgumentParser(description="Enter IP and Port to Connect to")
    parser.add_argument('-ip', type=str, default="127.0.0.1", required=True)
    parser.add_argument('-p', '-port', type=int, default=2020, required=True)
    parser.add_argument('-mynick', type=str, required=True)
    return parser.parse_args()


def send_message(msg):
    message_queue.put("{}:{}".format(ClientProtocol.MSG.value, msg))
    outputs.append(sock)


def request_name(name):
    message_queue.put("{}:{}".format(ServerProtocol.REGISTER.value, name))
    outputs.append(sock)


def request_group_access(group_name):
    message_queue.put("{}:{}".format(ServerProtocol.GACCESS.value, group_name))
    outputs.append(sock)


def request_group_table():
    print_debug("Requesting group-table...")
    message_queue.put("{}:".format(ServerProtocol.GROUPS.value))
    outputs.append(sock)


def create_group(name, ip, port):
    message_queue.put("{}:{}_{}_{}".format(ServerProtocol.CRGROUP.value, name, ip, port))
    outputs.append(sock)


def establish_connection(group_info):
    if group_info:
        ip, port = group_info.split("_")
        global CORRESPONDENT
        CORRESPONDENT = (ip, int(port))
        reconfigure_socket(ip)
        print_debug("Set Correspondent to {}".format(CORRESPONDENT))
        message_queue.put("{}:---{}--- Joined group!".format(ClientProtocol.MSG.value, args.mynick))
        outputs.append(sock)
    else:
        exit("Could not find group-name you requested on Server!")


def reconfigure_socket(group_ip):
    # In this version all clients need to use same port
    print_debug("Reconfigure Socket with ip {}".format(group_ip))
    val = struct.pack('4sL', socket.inet_aton(group_ip), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, val)


if __name__ == "__main__":
    args = parse_args()

    if not port_valid(args.p):
        exit("Port {} is not in range!".format(args.p))

    inputs = [sys.stdin]
    outputs = []
    message_queue = queue.Queue()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', int(args.p) + 1))
    inputs.append(sock)

    # First set correspondent to the server
    CORRESPONDENT = (args.ip, args.p)

    # Send requests to server
    print_debug("Send requests to Server...")
    request_name(args.mynick)

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
                    elif toHandle[0] == ClientProtocol.GRPINFO.value:
                        establish_connection(toHandle[1])
                    elif toHandle[0] == ClientProtocol.MSG.value:
                        print("msg: {}".format(toHandle[1]))
                    elif toHandle[0] == ClientProtocol.GRPTABLE.value:
                        if toHandle[1]:
                            [print(i) for i in toHandle[1].split("_")]
                        else:
                            print("Grouptable on server is empty!")
                    elif toHandle[0] == ClientProtocol.GRPCREATED.value:
                        if toHandle[1]:
                            print("Successfully created Group {}".format(toHandle[1]))
                        else:
                            print("Wasn't able to create group!")
                    else:
                        print_debug("Invalid Command received: {}".format(toHandle[0]))
            elif r is sys.stdin:
                read = sys.stdin.readline()
                if read.startswith("cmd:groups"):
                    request_group_table()
                elif read.startswith("cmd:enter"):
                    request_group_access(read.split(" ")[1])
                elif read.startswith("cmd:create"):
                    create_group(* read.split(" "))
                else:
                    send_message(sys.stdin.readline())
                if sock not in outputs:
                    outputs.append(sock)

        for w in writeable:
            if message_queue.empty():
                outputs.remove(w)
            else:
                print_debug("Sending to {}".format(CORRESPONDENT))
                w.sendto(message_queue.get_nowait().encode(), CORRESPONDENT)

        for e in exceptional:
            exit("Exception!")
            inputs.remove(e)
            if e in outputs:
                outputs.remove(e)
            e.close()
