PyGCN
=====

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
