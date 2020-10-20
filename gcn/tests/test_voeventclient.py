import pytest

from ..voeventclient import _validate_host_port


@pytest.mark.parametrize('host', ['a', ['a'], ('a',)])
@pytest.mark.parametrize('port', [1, [1], (1,)])
def test_validate_one_host_one_port(host, port):
    hosts, ports = _validate_host_port(host, port)
    assert list(hosts) == ['a']
    assert list(ports) == [1]


@pytest.mark.parametrize('host', [['a', 'b'], ('a', 'b')])
@pytest.mark.parametrize('port', [1, [1], (1,)])
def test_validate_many_hosts_one_port(host, port):
    hosts, ports = _validate_host_port(host, port)
    assert list(hosts) == ['a', 'b']
    assert list(ports) == [1, 1]


@pytest.mark.parametrize('host', ['a', ['a'], ('a',)])
@pytest.mark.parametrize('port', [[1, 2], (1, 2)])
def test_validate_one_host_many_ports(host, port):
    hosts, ports = _validate_host_port(host, port)
    assert list(hosts) == ['a', 'a']
    assert list(ports) == [1, 2]


@pytest.mark.parametrize('host', [['a', 'b'], ('a', 'b')])
@pytest.mark.parametrize('port', [[1, 2], (1, 2)])
def test_validate_many_hosts_many_ports(host, port):
    hosts, ports = _validate_host_port(host, port)
    assert list(hosts) == ['a', 'b']
    assert list(ports) == [1, 2]


def test_validate_mismatched_numbers_of_hosts_and_ports():
    host = ['a', 'b']
    port = [1, 2, 3]
    with pytest.raises(ValueError):
        _validate_host_port(host, port)
