#!/usr/bin/env python3

"""
udp_client: Allows to chat with one other udp client or groups. It first connects to a udp_server and register itself
            and requests the connection information from a peer or group. When the server response with valid
            connection-info then you can start chatting.
            Multicast IPS: 224.0.0.0 through 230.255.255.255
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
NICKNAME = None
SERVER = None
GROUP = None


def parse_args():
    parser = argparse.ArgumentParser(description="Enter IP and Port to Connect to")
    parser.add_argument('-ip', type=str, default="127.0.0.1", required=True)
    parser.add_argument('-p', '-port', type=int, default=2020, required=True)
    parser.add_argument('-mp', '-myport', type=int, required=True)
    return parser.parse_args()


def send_message(msg):
    message_queue.put(("{}:{}".format(ClientProtocol.MSG.value, msg), GROUP))
    outputs.append(chatSock)


def request_name(name):
    message_queue.put(("{}:{}".format(ServerProtocol.REGISTER.value, name), SERVER))
    outputs.append(ServerSock)


def request_group_access(group_name):
    message_queue.put(("{}:{}".format(ServerProtocol.GACCESS.value, group_name), SERVER))
    outputs.append(ServerSock)


def request_group_table():
    print_debug("Requesting group-table...")
    message_queue.put(("{}:".format(ServerProtocol.GROUPS.value), SERVER))
    outputs.append(ServerSock)


def create_group(name, ip, port):
    message_queue.put(("{}:{}_{}_{}".format(ServerProtocol.CRGROUP.value, name, ip, port), SERVER))
    outputs.append(ServerSock)


def establish_connection(group_info):
    if group_info:
        ip, port = group_info.split("_")
        global GROUP
        GROUP = (ip, int(port))
        reconfigure_socket(ip, port)
        print_debug("Set Correspondent to {}".format(GROUP))
        send_message("Hey there I am {}".format(NICKNAME))
    else:
        print("Could not find group-name you requested on Server!")


def reconfigure_socket(group_ip, group_port):
    # In this version all clients need to use same port
    print_debug("Configure chatsocket with ip {}".format(group_ip))
    global chatSock
    chatSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    val = struct.pack('4sL', socket.inet_aton(group_ip), socket.INADDR_ANY)
    # set socket to work on multicast Address
    chatSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, val)
    chatSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
    # configure socket, so that address can be reused
    chatSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    chatSock.bind(('', int(group_port)))
    inputs.append(chatSock)


if __name__ == "__main__":
    args = parse_args()

    if not port_valid(args.p):
        exit("Port {} is not in range!".format(args.p))

    inputs = [sys.stdin]
    outputs = []
    message_queue = queue.Queue()

    # Create Socket to Communicate with Server
    ServerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ServerSock.bind(('localhost', int(args.mp)))
    inputs.append(ServerSock)

    # Create Socket for Multicast group-chats
    chatSock = None

    # First set correspondent to the server
    SERVER = (args.ip, args.p)

    while inputs:
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)
        for r in readable:
            if r in [ServerSock, chatSock]:
                data, addr = r.recvfrom(BUFFER_SIZE)
                print_debug("Received data from {}".format(addr))
                if data:
                    toHandle = data.decode().split(":")
                    if toHandle[0] == ClientProtocol.LOGINDATA.value:
                        if toHandle[1]:
                            print("Your nickname on the server is: {}".format(toHandle[1]))
                            NICKNAME = toHandle[1]
                        else:
                            print("Failed to Register on Server, name already occupied!")
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
                    request_group_access(read.split(" ")[1][0:-1])
                elif read.startswith("cmd:create"):
                    create_group(read.split(" ")[1], read.split(" ")[2], read.split(" ")[3][0:-1])
                elif read.startswith("cmd:register"):
                    request_name(read.split(" ")[1])
                elif chatSock:
                    send_message(read)

        for w in writeable:
            if message_queue.empty():
                outputs.remove(w)
            else:
                text, dest = message_queue.get_nowait()
                print_debug("Sending to {}".format(dest))
                w.sendto(text.encode(), dest)

        for e in exceptional:
            exit("Exception!")
            inputs.remove(e)
            if e in outputs:
                outputs.remove(e)
            e.close()
