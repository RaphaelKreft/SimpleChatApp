#!/usr/bin/env python3

"""
tcp_direct.py is the main script for Task 1: It runs a chat based on TCP direct connection
"""

import argparse
import socket
import select
import sys

try:
    import queue
except ImportError:
    import Queue as queue

__author__ = "Tim Bachmann, Raphael Kreft"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Raphael Kreft"
__email__ = "r.kreft@unibas.ch"
__status__ = "Production"

BUFFERSIZE = 1024


def parse_args():
    parser = argparse.ArgumentParser(description="Enter IP and Port to Connect to")
    parser.add_argument('-ip', type=str, default="127.0.0.1", required=True)
    parser.add_argument('-p', '-port', type=int, default=2020, required=True)
    parser.add_argument('-mp', '-myport', type=int, default=2020, required=True)
    return parser.parse_args()


def port_valid(port):
    return 65536 > port > 1024


def handle_client_input(dest, data):
    print("Message from: {0} \n>>> {1} \n".format(dest, data.decode()))


if __name__ == "__main__":
    args = parse_args()

    if not port_valid(args.p):
        exit("Port {} is not in range!".format(args.p))

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(3)

    inputs = [sys.stdin]
    outputs = []
    message_queue = queue.Queue()

    # Try to Connect to Peer
    print('Try to Connect to {0} on port {1}'.format(args.ip, args.p))
    try:
        # conn.bind(("localhost", int(args.mp)))
        conn.connect((args.ip, args.p))
        conn.settimeout(0)
        inputs.append(conn)
        sock = None
        print("successfully connected to {}".format(args.ip))
    except IOError:
        # If Connection not Successful start to listen for incoming Connections
        print("Connection not successful, starting server and listen for incoming Connections!...")
        conn.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.bind(("localhost", int(args.mp)))
        sock.listen(1)
        inputs.append(sock)

    while inputs:
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)
        for r in readable:
            if r is sock:  # Accept new Connection
                conn, addr = r.accept()
                print("New Connection from {}".format(addr))
                conn.setblocking(False)
                inputs.append(conn)
            elif r is sys.stdin:
                message_queue.put(sys.stdin.readline().encode())
                if conn not in outputs:
                    outputs.append(conn)
            else:  # client has new data
                data = r.recv(BUFFERSIZE)
                if data:
                    handle_client_input(r.getpeername(), data)
                else:
                    inputs.remove(r)
                    if r in outputs:
                        outputs.remove(r)
                    r.close()

        for w in writeable:
            if not message_queue.empty():
                print("Try to send...")
                w.send(message_queue.get_nowait())
            else:
                outputs.remove(w)

        for e in exceptional:
            print("Exception!")
            inputs.remove(e)
            if e in outputs:
                outputs.remove(e)
            e.close()
