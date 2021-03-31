#!/usr/bin/env python3

"""
client_protocol.py: contains all instructions the client understands
"""

from enum import Enum

__author__ = "Tim Bachmann, Raphael Kreft"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Raphael Kreft"
__email__ = "r.kreft@unibas.ch"
__status__ = "Production"


class ClientProtocol(Enum):
    PEERINFO = "PIN"    # Server returned Info about other Client
    LOGINDATA = "LIN"   # Server returns Client's Nickname (Answer to REQ)
    MSG = "MSG"         # New Message from other client
    GRPINFO = "GRI"     # Server returned Connection-details of a specific Multicast Domain/Group
    GRPTABLE = "GTA"    # Server returned
    GRPCREATED = "GCR"  # Server returned if group has been created
