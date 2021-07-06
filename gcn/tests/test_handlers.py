import os
from urllib.parse import quote_plus

try:
    from importlib import resources
except ImportError:
    # FIXME: remove after dropping support for Python < 3.7
    import importlib_resources as resources

from lxml.etree import fromstring

from . import data
from .. import handlers
from .. import notice_types

try:
    import queue
except:
    import Queue as queue

payloads = [resources.read_binary(data, 'gbm_flt_pos.xml'),
            resources.read_binary(data, 'kill_socket.xml')]


def test_include_notice_types():
    t = []

    @handlers.include_notice_types(notice_types.FERMI_GBM_FLT_POS)
    def handler(payload, root):
        t.append(handlers.get_notice_type(root))

    for payload in payloads:
        handler(payload, fromstring(payload))

    assert t == [notice_types.FERMI_GBM_FLT_POS]


def test_exclude_notice_types():
    t = []

    @handlers.exclude_notice_types(notice_types.FERMI_GBM_FLT_POS)
    def handler(payload, root):
        t.append(handlers.get_notice_type(root))

    for payload in payloads:
        handler(payload, fromstring(payload))

    assert t == [notice_types.KILL_SOCKET]


def test_archive(tmpdir):
    try:
        old_dir = os.getcwd()
        os.chdir(str(tmpdir))

        for payload in payloads:
            handlers.archive(payload, fromstring(payload))

        for payload in payloads:
            root = fromstring(payload)
            filename = quote_plus(root.attrib['ivorn'])
            assert (tmpdir / filename).exists()
    finally:
        os.chdir(old_dir)


def test_queuehandler():
    queue_ = queue.Queue()
    queuehandler = handlers.queuehandlerfor(queue_)
    assert queue_.empty()

    for payload in payloads:
        queuehandler(payload, fromstring(payload))
        qpayload, qtree = queue_.get()
        assert qpayload == payload

    assert queue_.empty()

    for payload in payloads:
        queuehandler(payload, fromstring(payload))
    for payload in payloads:
        qpayload, qtree = queue_.get()
        assert qpayload == payload

    assert queue_.empty()
