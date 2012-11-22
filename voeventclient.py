#!/usr/bin/env python
import socket
import struct
import time
import xml.etree.cElementTree as ElementTree
import logging
import datetime
import threading


# Buffer for storing message size
size_struct = struct.Struct("!I")
size_len = size_struct.size

def get_now_iso8601():
    return datetime.datetime.now().isoformat()

class VOEventClient(threading.Thread):

    def __init__(self, host="68.169.57.253", port=8099, ivorn="ivo://astro.caltech.edu/leo.singer", iamalive_timeout=70, max_reconnect_timeout=1024, log=None):
        super(VOEventClient, self).__init__()
        self.host = host
        self.port = port
        self.ivorn = ivorn
        self.iamalive_timeout = iamalive_timeout
        self.max_reconnect_timeout = max_reconnect_timeout
        if log is None:
            log = logging.getLogger(self.__class__.__name__)
        self.log = log

        self._receipt_template = ElementTree.fromstring("""<?xml version='1.0' encoding='UTF-8'?>
        <trn:Transport role="ack" version="1.0"
        xmlns:trn="http://telescope-networks.org/schema/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
        http://telescope-networks.org/schema/Transport-v1.1.xsd">
        <Origin></Origin>
        <Response></Response>
        <TimeStamp></TimeStamp>
        </trn:Transport>
        """)
        self._receipt_template.find("Response").text = self.ivorn
        self._receipt_template_origin = self._receipt_template.find("Origin")
        self._receipt_template_timestamp = self._receipt_template.find("TimeStamp")


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
                self.log.info("opened socket")

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

    def _form_iamalive_response(self, root):
        root.attrib["role"] = "iamalive"
        response = ElementTree.Element("Response")
        response.text = self.ivorn
        root.append(response)
        timestamp = root.find("TimeStamp")
        if timestamp is None:
            timestamp = ElementTree.Element("TimeStamp")
            root.append(timestamp)
        timestamp.text = get_now_iso8601()
        return buffer(ElementTree.tostring(root))

    def _form_receipt_response(self, root):
        self._receipt_template_origin.text = root.attrib["ivorn"]
        self._receipt_template_timestamp = get_now_iso8601()
        return buffer(ElementTree.tostring(self._receipt_template))

    def _ingest_packet(self, sock):
        # Receive payload
        payload = self._recv_packet(sock)
        self.log.info("received packet of %d bytes", len(payload))
        self.log.debug("payload is:\n%s", payload)

        # Parse payload and act on it
        root = ElementTree.fromstring(payload)
        if root.tag == "{http://telescope-networks.org/schema/Transport/v1.1}Transport":
            if "role" not in root.attrib:
                self.log.error("receieved transport message without a role")
            elif root.attrib["role"] == "iamalive":
                self.log.info("received iamalive message")
                self._send_packet(sock, self._form_iamalive_response(root))
                self.log.info("sent iamalive response")
            else:
                self.log.error("received transport message with unrecognized role: %s", root.attrib["role"])
        elif root.tag == "{http://www.ivoa.net/xml/VOEvent/v2.0}VOEvent":
            self.log.info("received VOEvent")
            self._send_packet(sock, self._form_receipt_response(root))
            self.log.info("sent receipt response")
        else:
            self.log.error("received XML document with unrecognized root tag: %s", root.tag)

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
    # Set up logger
    logging.basicConfig()
    log = logging.getLogger("gcn")
    log.setLevel(logging.INFO)

    VOEventClient(log=log).run()
