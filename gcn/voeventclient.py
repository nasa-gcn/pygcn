# Copyright (C) 2014  Leo Singer
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
Anonymous VOEvent client for receiving GCNs in XML format.
"""
__author__ = "Leo Singer <leo.singer@ligo.org>"


import socket
import struct
import time
import xml.etree.cElementTree as ElementTree
import logging
import datetime


# Buffer for storing message size
_size_struct = struct.Struct("!I")
_size_len = _size_struct.size


def _get_now_iso8601():
    """Get current date-time in ISO 8601 format."""
    return datetime.datetime.now().isoformat()


def _open_socket(host, port, iamalive_timeout, max_reconnect_timeout, log):
    # Establish a connection. Wait 1 second after the first failed attempt.
    # Double the timeout after each failed attempt thereafter, until the
    # timeout reaches MAX_RECONNECT_TIMEOUT.
    reconnect_timeout = 1
    while True:
        try:
            # Open socket
            sock = socket.socket()
            try:
                sock.settimeout(iamalive_timeout)
                log.debug("opened socket")

                # Connect to host
                sock.connect((host, port))
                log.info("connected to %s:%d", host, port)
            except socket.error:
                try:
                    sock.close()
                except socket.error:
                    log.exception("could not close socket")
                else:
                    log.info("closed socket")
                raise
        except socket.error:
            if reconnect_timeout < max_reconnect_timeout:
                reconnect_timeout <<= 1
            log.exception("could not connect to %s:%d, will retry in %d seconds", host, port, reconnect_timeout)
            time.sleep(reconnect_timeout)
        else:
            return sock


def _recvall(sock, n):
    ba = bytearray(n)
    mv = memoryview(ba)
    while n > 0:
        nreceived = sock.recv_into(mv, n)
        n -= nreceived
        mv = mv[nreceived:]
    return buffer(ba)


def _recv_packet(sock):
    # Receive and unpack size of payload to follow
    payload_len, = _size_struct.unpack_from(sock.recv(4))

    # Receive payload
    return _recvall(sock, payload_len)


def _send_packet(sock, payload):
    # Send size of payload to follow
    sock.sendall(_size_struct.pack(len(payload)))

    # Send payload
    sock.sendall(payload)


def _form_response(role, origin, response, timestamp):
    return '''<?xml version='1.0' encoding='UTF-8'?><trn:Transport role="''' + role + '''" version="1.0" xmlns:trn="http://telescope-networks.org/schema/Transport/v1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1 http://telescope-networks.org/schema/Transport-v1.1.xsd"><Origin>''' + origin + '''</Origin><Response>''' + response + '''</Response><TimeStamp>''' + timestamp + '''</TimeStamp></trn:Transport>'''


def _ingest_packet(sock, ivorn, handler, log):
    # Receive payload
    payload = _recv_packet(sock)
    log.debug("received packet of %d bytes", len(payload))
    log.debug("payload is:\n%s", payload)

    # Parse payload and act on it
    root = ElementTree.fromstring(payload)
    if root.tag == "{http://telescope-networks.org/schema/Transport/v1.1}Transport":
        if "role" not in root.attrib:
            log.error("receieved transport message without a role")
        elif root.attrib["role"] == "iamalive":
            log.debug("received iamalive message")
            _send_packet(sock, _form_response("iamalive", root.find("Origin").text, ivorn, _get_now_iso8601()))
            log.debug("sent iamalive response")
        else:
            log.error("received transport message with unrecognized role: %s", root.attrib["role"])
    elif root.tag in {"{http://www.ivoa.net/xml/VOEvent/v1.1}VOEvent", "{http://www.ivoa.net/xml/VOEvent/v2.0}VOEvent"}:
        log.info("received VOEvent")
        _send_packet(sock, _form_response("ack", root.attrib["ivorn"], ivorn, _get_now_iso8601()))
        log.debug("sent receipt response")
        if handler is not None:
            handler(payload, root)
    else:
        log.error("received XML document with unrecognized root tag: %s", root.tag)


def listen(host="68.169.57.253", port=8099, ivorn="ivo://python_voeventclient/anonymous", iamalive_timeout=150, max_reconnect_timeout=1024, handler=None, log=None):
    if log is None:
        log = logging.getLogger('gcn.listen')

    while True:
        sock = _open_socket(host, port, iamalive_timeout, max_reconnect_timeout, log)

        try:
            while True:
                _ingest_packet(sock, ivorn, handler, log)
        except socket.timeout:
            log.warn("timed out")
        finally:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except socket.error:
                log.exception("could not shut down socket")

            try:
                sock.close()
            except socket.error:
                log.exception("could not close socket")
            else:
                log.info("closed socket")
