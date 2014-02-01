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
import threading
import Queue
import urllib


class PayloadHandler(threading.Thread):
    """Base class for payload handling worker thread."""

    def __init__(self, log=None):
        super(PayloadHandler, self).__init__()
        if log is None:
            log = logging.getLogger(self.__class__.__name__)
        self.log = log
        self._queue = Queue.Queue()
        self.put = self._queue.put

    def finish(self):
        """Put None on the queue, to tell the thread to stop."""
        self.put(None)
        self.join()

    def handlePayload(self, payload, root):
        """Handle one payload."""
        raise NotImplementedError

    def run(self):
        self.log.info("started")
        for args in iter(self._queue.get, None):
            try:
                self.handlePayload(*args)
            except:
                self.log.exception('exception in handler')
            self._queue.task_done()
        self.log.info("finished")


class ArchivingPayloadHandler(PayloadHandler):
    """Payload handler that archives VOEvent messages as files in the current
    working directory. The filename is a URL-escaped version of the messages'
    IVORN."""

    def handlePayload(self, payload, root):
        ivorn = root.attrib['ivorn']
        filename = urllib.quote_plus(ivorn)
        with open(filename, "w") as f:
            f.write(payload)
        self.log.info("archived %s", ivorn)

