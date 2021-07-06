# Copyright (C) 2013-2018  Leo Singer
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
Anonymous VOEvent client for receiving GCN/TAN notices in XML format

The Gamma-ray Coordinates Network/Transient Astronomy Network (GCN/TAN,
http://gcn.gsfc.nasa.gov) is a system for distributing astronomical alerts,
largely focused on operations of and detections from high-energy satellite
missions.

GCN/TAN disseminates both Notices (prompt, machine-readable alerts) and
Circulars (human-readable correspondence) through a handful of delivery methods
and formats.

This package implements a simple client that anonymously listens for VOEvent
(http://www.ivoa.net/documents/VOEvent) XML format notices over the custom
TCP/IP VOEvent Transport Protocol
(http://www.ivoa.net/documents/Notes/VOEventTransport).
"""

from . import handlers
from . import notice_types
from . import voeventclient
from ._version import version as __version__  # noqa: F401
from .handlers import *  # noqa: F401, F403
from .notice_types import *  # noqa: F401, F403
from .voeventclient import *  # noqa: F401, F403

__all__ = handlers.__all__ + notice_types.__all__ + voeventclient.__all__
