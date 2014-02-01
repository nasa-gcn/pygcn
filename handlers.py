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

