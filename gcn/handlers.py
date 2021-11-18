# Copyright (C) 2014-2018  Leo Singer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Payload handlers.
"""

import functools
import logging
from urllib.parse import quote_plus

__all__ = ('get_notice_type', 'include_notice_types', 'exclude_notice_types',
           'archive')


def get_notice_type(root):
    return int(root.find("./What/Param[@name='Packet_Type']").attrib['value'])


def include_notice_types(*notice_types):
    """Process only VOEvents whose integer GCN packet types are in
    `notice_types`. Should be used as a decorator, as in:

        import gcn.handlers
        import gcn.notice_types as n

        @gcn.handlers.include_notice_types(n.FERMI_GBM_GND_POS,
                                           n.FERMI_GBM_FIN_POS)
        def handle(payload, root):
            print('Got notice of type FERMI_GBM_GND_POS or FERMI_GBM_FIN_POS')
    """
    notice_types = frozenset(notice_types)

    def decorate(handler):
        @functools.wraps(handler)
        def handle(payload, root, *args, **kwargs):
            if get_notice_type(root) in notice_types:
                handler(payload, root, *args, **kwargs)
        return handle
    return decorate


def exclude_notice_types(*notice_types):
    """Process only VOEvents whose integer GCN packet types are not in
    `notice_types`. Should be used as a decorator, as in:

        import gcn.handlers
        import gcn.notice_types as n

        @gcn.handlers.exclude_notice_types(n.FERMI_GBM_GND_POS,
                                           n.FERMI_GBM_FIN_POS)
        def handle(payload, root):
            print('Got notice not of type FERMI_GBM_GND_POS '
                  'or FERMI_GBM_FIN_POS')
    """
    notice_types = frozenset(notice_types)

    def decorate(handler):
        @functools.wraps(handler)
        def handle(payload, root, *args, **kwargs):
            if get_notice_type(root) not in notice_types:
                handler(payload, root, *args, **kwargs)
        return handle
    return decorate


def archive(payload, root):
    """Payload handler that archives VOEvent messages as files in the current
    working directory. The filename is a URL-escaped version of the messages'
    IVORN."""
    ivorn = root.attrib['ivorn']
    filename = quote_plus(ivorn)
    with open(filename, 'wb') as f:
        f.write(payload)
    logging.getLogger('gcn.handlers.archive').info("archived %s", ivorn)
