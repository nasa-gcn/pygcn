# Copyright (C) 2014  Leo Singer
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Payload handlers.
"""
__author__ = "Leo Singer <leo.singer@ligo.org>"


import logging
import urllib


class include_notice_types(object):
    """Process only VOEvents whose integer GCN packet types are in
    `included`."""
    def __init__(self, included, handler):
        self.included = included
        self.handler = handler
    def __call__(self, payload, root):
        packet_type = int(root.find("./What/Param[@name='Packet_Type']").attrib['value'])
        if packet_type in self.included:
            self.handler(payload, root)


class exclude_notice_types(object):
    """Process only VOEvents whose integer GCN packet types are not in
    `excluded`."""
    def __init__(self, excluded, handler):
        self.excluded = excluded
        self.handler = handler
    def __call__(self, payload, root):
        packet_type = int(root.find("./What/Param[@name='Packet_Type']").attrib['value'])
        if packet_type not in self.excluded:
            self.handler(payload, root)


def archive(payload, root):
    """Payload handler that archives VOEvent messages as files in the current
    working directory. The filename is a URL-escaped version of the messages'
    IVORN."""
    ivorn = root.attrib['ivorn']
    filename = urllib.quote_plus(ivorn)
    with open(filename, "w") as f:
        f.write(payload)
    logging.getLogger('gcn.handlers.archive').info("archived %s", ivorn)

