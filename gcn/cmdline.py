# Copyright (C) 2016  Leo Singer
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Utilities for command-line interface.
"""
__author__ = "Leo Singer <leo.singer@ligo.org>"


import argparse
import collections


class HostPort(collections.namedtuple('HostPort', 'host port')):

    def __new__(cls, string, default_host, default_port):
        host, _, port = string.partition(':')
        if not host:
            host = default_host
        if not port:
            port = default_port
        port = int(port)
        return super(HostPort, cls).__new__(cls, host, port)


class HostPortType(object):

    def __init__(self, default_host, default_port):
        self.default_host = default_host
        self.default_port = default_port

    def __call__(self, string):
        return HostPort(string, self.default_host, self.default_port)

    def __repr__(self):
        return 'host:port'


class HostPortAction(argparse._StoreAction):

    def __init__(self, *args, **kwargs):
        default = kwargs.get('default', '')
        default_host, _, default_port = default.partition(':')
        metavar = 'HOST' + ('[:PORT]' if default_port else ':PORT')
        nargs = '?' if default_host and default_port else 1
        type = HostPortType(default_host, default_port)
        super(HostPortAction, self).__init__(
            *args, metavar=metavar, nargs=nargs, type=type, **kwargs)
