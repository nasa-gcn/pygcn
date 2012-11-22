#!/usr/bin/env python
import sys
import socket
import struct
import time
import xml.etree.cElementTree as ElementTree
import logging
import datetime


HOST = "68.169.57.253"
PORT = 8099


MY_IVORN = "ivo://astro.caltech.edu/leo.singer"


IAMALIVE_TIMEOUT = 70
MAX_RECONNECT_TIMEOUT = 1024


# Set up logger
logging.basicConfig()
log = logging.getLogger("gcn")
log.setLevel(logging.DEBUG)

# Buffer for storing message size
size_struct = struct.Struct("!I")
size_len = size_struct.size
size_bytes = bytearray(size_len)
size_buf = buffer(size_bytes)

# Buffer for storing payload
payload_capacity = 512
payload_bytes = bytearray(payload_capacity)
payload_mem = memoryview(payload_bytes)


def get_now_iso8601():
    return datetime.datetime.now().isoformat()


def form_iamalive_response(root):
    root.attrib["role"] = "iamalive"
    response = ElementTree.Element("Response")
    response.text = MY_IVORN
    root.append(response)
    timestamp = root.find("TimeStamp")
    if timestamp is None:
        timestamp = ElementTree.Element("TimeStamp")
        root.append(timestamp)
    timestamp.text = get_now_iso8601()
    return buffer(ElementTree.tostring(root))


receipt_template = ElementTree.fromstring("""<?xml version='1.0' encoding='UTF-8'?>
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
receipt_template.find("Response").text = MY_IVORN
receipt_template_origin = receipt_template.find("Origin")
receipt_template_timestamp = receipt_template.find("TimeStamp")


def form_receipt_response(root):
    receipt_template_origin.text = root.attrib["ivorn"]
    receipt_template_timestamp = get_now_iso8601()
    return buffer(ElementTree.tostring(receipt_template))


while True:
    # Attempt to connect. Wait 1 second after the first failed attempt. Double
    # the timeout after each failed attempt thereafter, until the timeout
    # reaches MAX_RECONNECT_TIMEOUT.
    reconnect_timeout = 1
    while True:
        try:
            # Open socket
            sock = socket.socket()
            sock.settimeout(IAMALIVE_TIMEOUT)
            log.info("opened socket")

            # Connect to host
            sock.connect((HOST, PORT))
            log.info("connected to %s:%d", HOST, PORT)
        except socket.error:
            if reconnect_timeout < MAX_RECONNECT_TIMEOUT:
                reconnect_timeout <<= 1
            log.exception("could not connect to %s:%d, will retry in %d seconds", HOST, PORT, reconnect_timeout)
            time.sleep(reconnect_timeout)
        else:
            break

    try:
        while True:
            # Read and unpack payload length
            sock.recv_into(size_bytes, 4)
            payload_len, = size_struct.unpack_from(size_buf)

            log.info("prepared to receive %d bytes", payload_len)

            # Resize payload buffer if necessary
            if payload_len > payload_capacity:
                while payload_len > payload_capacity:
                    payload_capacity <<= 1
                payload_bytes = bytearray(payload_capacity)
                payload_mem = memoryview(payload_bytes)

            # Receive all of payload
            payload_len_remaining = payload_len
            payload_mem_remaining = payload_mem
            while payload_len_remaining > 0:
                received_len = sock.recv_into(payload_mem_remaining, payload_len_remaining)
                payload_len_remaining -= received_len
                payload_mem_remaining = payload_mem_remaining[received_len:]

            # Echo packet
            payload = buffer(payload_bytes[:payload_len])
            log.debug("payload is:\n%s", payload)

            root = ElementTree.fromstring(payload)

            if root.tag == "{http://telescope-networks.org/schema/Transport/v1.1}Transport":
                if "role" not in root.attrib:
                    log.error("receieved transport message without a role")
                elif root.attrib["role"] == "iamalive":
                    log.info("received iamalive message")
                    response = form_iamalive_response(root)
                    sock.sendall(size_struct.pack(len(response)))
                    sock.sendall(response)
                    log.info("sent iamalive response")
                else:
                    log.error("received transport message with unrecognized role: %s", root.attrib["role"])
            elif root.tag == "{http://www.ivoa.net/xml/VOEvent/v2.0}VOEvent":
                log.info("received VOEvent")
                response = form_receipt_response(root)
                sock.sendall(size_struct.pack(len(response)))
                sock.sendall(response)
                log.info("sent receipt response")
            else:
                log.error("received unrecognized")
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
