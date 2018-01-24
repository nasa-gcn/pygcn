import pytest

from ..cmdline import listen_main, serve_main


def test_listen_main():
    # FIXME: test more than just the argument parser!
    with pytest.raises(SystemExit):
        listen_main(['--version'])


def test_serve_main():
    # FIXME: test more than just the argument parser!
    with pytest.raises(SystemExit):
        serve_main(['--version'])
