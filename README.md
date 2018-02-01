# PyGCN

Anonymous VOEvent client for receiving GCN/TAN notices in XML format

[![Build Status](https://travis-ci.org/lpsinger/pygcn.svg?branch=master)](https://travis-ci.org/lpsinger/pygcn)

The [Gamma-ray Coordinates Network/Transient Astronomy Network (GCN/TAN)][1] is
a system for distributing astronomical alerts, largely focused on operations of
and detections from high-energy satellite missions.

GCN/TAN disseminates both Notices (prompt, machine-readable alerts) and
Circulars (human-readable correspondence) through a handful of delivery methods
and formats.

This package implements a simple client that listens for [VOEvent][2] XML
format notices over the custom TCP/IP [VOEvent Transport Protocol][3]. By
default, it connects to one of the anonymous GCN/TAN server, so no sign-up
or configuration is necessary to begin receiving alerts.

## Installation

To install PyGCN, simply run:

    $ pip install --user pygcn

## Usage

PyGCN provides an example script called `pygcn-listen` that will simply write
all VOEvents that it receives to files in the current directory. To try it out,
simply run:

    $ pygcn-listen

and then type Control-C to quit.

## Writing a custom GCN handler

You can also write your own handler that performs a custom action for every GCN
that is received. A handler function takes two arguments: `payload`, the raw
content of the GCN, and `root`, the root element of the XML document as parsed
by ['lxml.etree``][5]. Here is a basic example:

```python
#!/usr/bin/env python
import gcn

# Define your custom handler here.
def handler(payload, root):
    # Get the IVORN, or unique VOEvent ID, and print it.
    print(root.attrib['ivorn'])

    # Print all of the event attributes.
    for param in root.findall('./What/Param'):
        name = param.attrib['name']
        value = param.attrib['value']
        print('{} = {}'.format(name, value))

# Listen for VOEvents until killed with Control-C.
gcn.listen(handler=handler)
```
## Filtering

You can also filter events by notice type using
`gcn.handlers.include_notice_types` or `gcn.handlers.exclude_notice_types`.
Here is an example:

```python
#!/usr/bin/env python
import gcn
import gcn.handlers
import gcn.notice_types

# Define your custom handler here.
@gcn.handlers.include_notice_types(
    gcn.notice_types.FERMI_GBM_FLT_POS,  # Fermi GBM localization (flight)
    gcn.notice_types.FERMI_GBM_GND_POS,  # Fermi GBM localization (ground)
    gcn.notice_types.FERMI_GBM_FIN_POS)  # Fermi GBM localization (final)
def handler(payload, root):
    # Look up right ascension, declination, and error radius fields.
    pos2d = root.find('.//{*}Position2D')
    ra = float(pos2d.find('.//{*}C1').text)
    dec = float(pos2d.find('.//{*}C2').text)
    radius = float(pos2d.find('.//{*}Error2Radius').text)

    # Print.
    print('ra = {:g}, dec={:g}, radius={:g}'.format(ra, dec, radius))

# Listen for VOEvents until killed with Control-C.
gcn.listen(handler=handler)
```


[1]: http://gcn.gsfc.nasa.gov
[2]: http://www.ivoa.net/documents/VOEvent
[3]: http://www.ivoa.net/documents/Notes/VOEventTransport
[4]: https://docs.python.org/2/library/xml.etree.elementtree.html
[5]: http://lxml.de
