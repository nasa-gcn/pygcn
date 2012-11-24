#!/usr/bin/env python
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
import threading
import urllib


# Buffer for storing message size
size_struct = struct.Struct("!I")
size_len = size_struct.size


def get_now_iso8601():
    return datetime.datetime.now().isoformat()


class VOEventClient(threading.Thread):

    def __init__(self, host="68.169.57.253", port=8099, ivorn="ivo://python_voeventclient/anonymous", iamalive_timeout=70, max_reconnect_timeout=1024, handlers=None, log=None):
        super(VOEventClient, self).__init__()
        self.host = host
        self.port = port
        self.ivorn = ivorn
        self.iamalive_timeout = iamalive_timeout
        self.max_reconnect_timeout = max_reconnect_timeout
        if log is None:
            log = logging.getLogger(self.__class__.__name__)
        self.log = log
        self._handlers = []
        if handlers is not None:
            self._handlers.extend(handlers)

    def _open_socket(self):
        """Establish a connection. Wait 1 second after the first failed attempt.
        Double the timeout after each failed attempt thereafter, until the
        timeout reaches MAX_RECONNECT_TIMEOUT."""
        reconnect_timeout = 1
        while True:
            try:
                # Open socket
                sock = socket.socket()
                sock.settimeout(self.iamalive_timeout)
                self.log.debug("opened socket")

                # Connect to host
                sock.connect((self.host, self.port))
                self.log.info("connected to %s:%d", self.host, self.port)
            except socket.error:
                if reconnect_timeout < self.max_reconnect_timeout:
                    reconnect_timeout <<= 1
                self.log.exception("could not connect to %s:%d, will retry in %d seconds", self.host, self.port, reconnect_timeout)
                time.sleep(reconnect_timeout)
            else:
                return sock

    @staticmethod
    def _recvall(sock, n):
        ba = bytearray(n)
        mv = memoryview(ba)
        while n > 0:
            nreceived = sock.recv_into(mv, n)
            n -= nreceived
            mv = mv[nreceived:]
        return buffer(ba)

    @staticmethod
    def _recv_packet(sock):
        # Receive and unpack size of payload to follow
        payload_len, = size_struct.unpack_from(sock.recv(4))

        # Receive payload
        return VOEventClient._recvall(sock, payload_len)

    @staticmethod
    def _send_packet(sock, payload):
        # Send size of payload to follow
        sock.sendall(size_struct.pack(len(payload)))

        # Send payload
        sock.sendall(payload)

    @staticmethod
    def _form_response(role, origin, response, timestamp):
        return '''<?xml version='1.0' encoding='UTF-8'?><trn:Transport role="''' + role + '''" version="1.0" xmlns:trn="http://telescope-networks.org/schema/Transport/v1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1 http://telescope-networks.org/schema/Transport-v1.1.xsd"><Origin>''' + origin + '''</Origin><Response>''' + response + '''</Response><TimeStamp>''' + timestamp + '''</TimeStamp></trn:Transport>'''

    def _form_iamalive_response(self, root):
        return self._form_response("iamalive", root.find("Origin").text, self.ivorn, get_now_iso8601())

    def _form_receipt_response(self, root):
        return self._form_response("ack", root.attrib["ivorn"], self.ivorn, get_now_iso8601())

    def _ingest_packet(self, sock):
        # Receive payload
        payload = self._recv_packet(sock)
        self.log.debug("received packet of %d bytes", len(payload))
        self.log.debug("payload is:\n%s", payload)

        # Parse payload and act on it
        root = ElementTree.fromstring(payload)
        if root.tag == "{http://telescope-networks.org/schema/Transport/v1.1}Transport":
            if "role" not in root.attrib:
                self.log.error("receieved transport message without a role")
            elif root.attrib["role"] == "iamalive":
                self.log.debug("received iamalive message")
                self._send_packet(sock, self._form_iamalive_response(root))
                self.log.debug("sent iamalive response")
            else:
                self.log.error("received transport message with unrecognized role: %s", root.attrib["role"])
        elif root.tag == "{http://www.ivoa.net/xml/VOEvent/v2.0}VOEvent":
            self.log.info("received VOEvent")
            self._send_packet(sock, self._form_receipt_response(root))
            self.log.debug("sent receipt response")
            for handler in self._handlers:
                handler.put(payload)
        else:
            self.log.error("received XML document with unrecognized root tag: %s", root.tag)

    def add_handler(self, handler):
        self._handlers.append(handler)

    def run(self):
        while True:
            sock = self._open_socket()

            try:
                while True:
                    self._ingest_packet(sock)
            except socket.timeout:
                self.log.warn("timed out")
            finally:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except socket.error:
                    self.log.exception("could not shut down socket")

                try:
                    sock.close()
                except socket.error:
                    self.log.exception("could not close socket")
                else:
                    self.log.info("closed socket")


if __name__ == "__main__":
    import handlers

    # Set up logger
    logging.basicConfig(level=logging.INFO)

    # Set up and start handler thread to save VOEvents to disk
    handler = handlers.ArchivingPayloadHandler()
    handler.start()

    try:
        # Set up and start client on main thread
        client = VOEventClient(handlers=[handler])
        client.run()
    finally:
        # Wait for archiving handler to finish processing all events in its queue
        handler.finish()

