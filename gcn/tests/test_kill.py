from importlib import resources
import logging
import socket
import threading
import time

from . import data
from .. import listen
from .. import voeventclient
from ..handlers import include_notice_types

# Set up logger
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

payloads = [resources.read_binary(data, 'gbm_flt_pos.xml'),
            resources.read_binary(data, 'kill_socket.xml')]


def serve(payloads, host='127.0.0.1', port=8099, retransmit_timeout=0,
          log=None):
    """Rudimentary GCN server, for testing purposes. Serves just one connection
    at a time, and repeats the same payloads in order, repeating, for each
    connection."""
    if log is None:
        log = logging.getLogger('gcn.serve')

    sock = socket.socket()
    try:
        sock.bind((host, port))
        log.info("bound to %s:%d", host, port)
        sock.listen(0)
        for i in range(5):
            conn, addr = sock.accept()
            log.info("connected to %s:%d", addr, port)
            try:
                for payload in payloads:
                    time.sleep(retransmit_timeout)
                    voeventclient._send_packet(conn, payload)
            except socket.error:
                log.exception('error communicating with peer')
            finally:
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except socket.error:
                    log.exception("could not shut down socket")

                try:
                    conn.close()
                except socket.error:
                    log.exception("could not close socket")
                else:
                    log.info("closed socket")
    finally:
        sock.close()


class MessageCounter(object):

    def __init__(self):
        self.count = 0

    def __call__(self, *args):
        self.count += 1


def test_reconnect_after_kill():
    """Test that the client recovers if the server closes the connection."""
    server_thread = threading.Thread(
        group=None, target=serve, args=(payloads,),
        kwargs=dict(retransmit_timeout=0.1))
    server_thread.daemon = True
    server_thread.start()

    handler = MessageCounter()

    client_thread = threading.Thread(
        group=None, target=listen,
        kwargs=dict(host='127.0.0.1', max_reconnect_timeout=4,
                    handler=include_notice_types(111)(handler)))
    client_thread.daemon = True
    client_thread.start()

    time.sleep(5)
    assert handler.count == 5
