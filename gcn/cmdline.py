# Copyright (C) 2016-2018  Leo Singer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Utilities for command-line interface.
"""
import argparse
import collections
import logging

from . import handlers, listen, serve, __version__


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
        kwargs = dict(kwargs)
        default = kwargs.pop('default', '')
        default_host, _, default_port = default.partition(':')
        metavar = 'HOST' + ('[:PORT]' if default_port else ':PORT')
        nargs = kwargs.pop(
            'nargs', '?' if default_host and default_port else 1)
        type = HostPortType(default_host, default_port)
        if nargs in {argparse.ZERO_OR_MORE, argparse.ONE_OR_MORE}:
            default = [type(default)]
        super(HostPortAction, self).__init__(
            *args, metavar=metavar, nargs=nargs, type=type, default=default,
            **kwargs)


def listen_main(args=None):
    """Example VOEvent listener that saves all incoming VOEvents to disk."""

    # Command line interface
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('addr', default='68.169.57.253:8099',
                        action=HostPortAction, nargs='*',
                        help='Server host and port; if multiple options are '
                        'provided, then loop over hosts until a connection '
                        'with one of them is established. '
                        '(default: %(default)s)')
    parser.add_argument('--version', action='version',
                        version='pygcn ' + __version__)
    args = parser.parse_args(args)

    # Set up logger
    logging.basicConfig(level=logging.INFO)

    # Listen for GCN notices (until interrupted or killed)
    host, port = [list(_) for _ in zip(*args.addr)]
    listen(host=host, port=port, handler=handlers.archive)


def serve_main(args=None):
    """Rudimentary GCN server, for testing purposes. Serves just one connection
    at a time, and repeats the same payloads in order, repeating, for each
    connection."""

    # Command line interface
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', dest='addr',
                        default='127.0.0.1:8099', action=HostPortAction,
                        help='Server host and port (default: %(default)s)')
    parser.add_argument('--retransmit-timeout', '-t', metavar='SECONDS',
                        type=int, default=1,
                        help='Delay between packets (default: %(default)s)')
    parser.add_argument('payloads', nargs='+', metavar='PAYLOAD.xml')
    parser.add_argument('--version', action='version',
                        version='pygcn ' + __version__)
    args = parser.parse_args(args)

    # Set up logger
    logging.basicConfig(level=logging.INFO)

    # Serve GCN notices (until interrupted or killed)
    serve(args.payloads, host=args.addr.host, port=args.addr.port,
          retransmit_timeout=args.retransmit_timeout)
