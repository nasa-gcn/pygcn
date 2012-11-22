#!/usr/bin/env python
import sys
import socket
import struct
import logging


HOST = "68.169.57.253"
PORT = 8099


# Set up logger
logging.basicConfig()
log = logging.getLogger("gcn")
log.setLevel(logging.INFO)

# Buffer for storing message size
size_struct = struct.Struct("!I")
size_len = size_struct.size
size_bytes = bytearray(size_len)
size_buf = buffer(size_bytes)

# Buffer for storing payload
payload_capacity = 512
payload_bytes = bytearray(payload_capacity)
payload_mem = memoryview(payload_bytes)

# Open socket
log.info("opening socket")
sock = socket.socket()

# Connect to host
sock.connect((HOST, PORT))
log.info("connecting to %s:%d", HOST, PORT)

while True:
    # Read and unpack payload length
    log.info("waiting for next GCN")
    sock.recv_into(size_bytes, 4)
    payload_len, = size_struct.unpack_from(size_buf)

    log.info("preparing to receive %d bytes", payload_len)

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
    log.info("recieved packet, payload is:\n%s", payload_bytes[:payload_len])
