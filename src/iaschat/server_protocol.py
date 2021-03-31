#!/usr/bin/env python3

"""
server_protocol.py: contains all instructions the server understands
"""

from enum import Enum

__author__ = "Tim Bachmann, Raphael Kreft"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Raphael Kreft"
__email__ = "r.kreft@unibas.ch"
__status__ = "Production"


class ServerProtocol(Enum):
    REGISTER = "REG"
    REQUEST = "REQ"
