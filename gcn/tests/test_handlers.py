import os
import pkg_resources
from six.moves.urllib.parse import quote_plus

from ..voeventclient import parse_from_string
from .. import handlers
from .. import notice_types


payloads = [pkg_resources.resource_string(__name__, 'data/gbm_flt_pos.xml'),
            pkg_resources.resource_string(__name__, 'data/kill_socket.xml')]


def test_include_notice_types():
    t = []

    @handlers.include_notice_types(notice_types.FERMI_GBM_FLT_POS)
    def handler(payload, root):
        t.append(handlers.get_notice_type(root))

    for payload in payloads:
        handler(payload, parse_from_string(payload))

    assert t == [notice_types.FERMI_GBM_FLT_POS]


def test_exclude_notice_types():
    t = []

    @handlers.exclude_notice_types(notice_types.FERMI_GBM_FLT_POS)
    def handler(payload, root):
        t.append(handlers.get_notice_type(root))

    for payload in payloads:
        handler(payload, parse_from_string(payload))

    assert t == [notice_types.KILL_SOCKET]


def test_archive(tmpdir):
    try:
        old_dir = os.getcwd()
        os.chdir(str(tmpdir))

        for payload in payloads:
            handlers.archive(payload, parse_from_string(payload))

        for payload in payloads:
            root = parse_from_string(payload)
            filename = quote_plus(root.attrib['ivorn'])
            assert (tmpdir / filename).exists()
    finally:
        os.chdir(old_dir)
