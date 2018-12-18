#!venv/bin python
# -*- coding: UTF-8 -*-

"""
This script defines [GenericUDPClient], [GenericTCPClient], [GenericClientFactory],
                    [GenericUDPServer], [GenericTCPServer], [GenericServerFactory]
The goal of this library is to make [twisted] as easy to use as [PodSixNet]

Written by Grant Yang (2018)
"""

from .udp import *
from .tcp import *
from .cUDP import *

__all__ = ['GenericUDPClient', 'GenericTCPClient', 'GenericClientFactory', 'reactor',
           'GenericUDPServer', 'GenericTCPServer', 'GenericServerFactory']
