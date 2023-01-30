# Changelog

## 1.1.3 (2022-07-20)

- The `@include_notice_type` and `@exclude_notice_type` decorators now pass
  through all arguments to the wrapped function. [David Palmer]

- Move the repository to https://github.com/nasa-gcn/pygcn. [Leo Singer]

- Add notice types for GECAM. [Leo Singer]

## 1.1.2 (2021-12-22)

- Run unit tests under Python 3.10. [Leo Singer]

- Drop support for Python 3.6, which reached end of life on 2021-12-23.
  [Leo Singer]

- Remove setup.py file. [Leo Singer]

## 1.1.1 (2021-04-20)

- Remove use of the third-party `pkg_resources` module from unit tests and
  use Python standard library module `importlib.resources` instead.
  [Leo Singer]

- Add new notice type: `SK_SN`. [Leo Singer]

- Rename the development branch from `master` to `main`. [Leo Singer]

## 1.1.0 (2021-01-29)

- Add new notice types: `AMON_NU_EM_COINC`, `ICECUBE_CASCADE`.
 [Volodymyr Savchenko]

- Drop support for Python 2.7 and 3.5, which have reached end-of-life.
  Add support for Python 3.9. [Leo Singer]

## 1.0.2 (2020-03-05)

- Fix incorrect license filename in setup.cfg. [Leo Singer]

## 1.0.1 (2020-03-05)

- Add new notice type: `LVC_EARLY_WARNING`. [Leo Singer]

- Update license to GPL-3+. [Leo Singer]

## 1.0.0 (2020-01-29)

- The `gcn.listen` method can now cycle through a list of remote hosts when
  re-establishing the connection to GCN. [Varun Bhalerao, Aaron Jones]

- Add new notice types: `AGILE_MCAL_ALERT`, `GWHEN_COINC`. [Leo Singer]

## 0.1.20 (2019-02-12)

- Add new notice types: `HAWC_BURST_MONITOR`, `ICECUBE_ASTROTRACK_GOLD`,
  and `ICECUBE_ASTROTRACK_BRONZE`. [Vladimir Savchenko]

## 0.1.19 (2019-02-12)

- Add the `LVC_RETRACTION` notice type. [Leo Singer]

## 0.1.18 (2018-12-11)

- Add `{http://telescope-networks.org/xml/Transport/v1.1}Transport` and
  `{http://telescope-networks.org/schema/Transport/v1.1}Transport` as
  recognized VOEvent Transport Protocol namespaces to support the 4pisky and
  comet brokers. [reported by Martin Dyer]

## 0.1.17 (2018-10-04)

- Add missing dependency on six. [Leo Singer]

- Fix handling of payload command line arguments for pygcn-server.
  Thanks go out to WeiKang Zheng of UC Berkeley for reporting this.
  [Leo Singer]

## 0.1.16 (2018-03-03)

- Add `functools.wraps()` to handler decorators so that the original
  function docstrings are preserved. [Leo Singer]

## 0.1.15 (2018-02-10)

- Update module __all__ variables for convenience. [Leo Singer]

- Add experimental PEP 435 style enum class, `gcn.NoticeType`. [Leo Singer]

## 0.1.14 (2018-02-01)

- Depend unconditionally on lxml. Some of the examples depend on it because
  of differences in how xml.etree and lxml.etree handle XML namespaces.
  [Leo Singer]

## 0.1.13 (2018-01-24)

- Include missing test data in package. [Leo Singer]

## 0.1.12 (2018-01-24)

- Make source PEP8 compliant. [Leo Singer]

- Update list of GCN notice types. [Leo Singer]

- Fix some lingering Python 3 issues. [Leo Singer]

- Convert `pygcn-listen` and `pygcn-serve` from scripts into
  console entry points. [Leo Singer]

- Improve unit test coverage. [Leo Singer]

## 0.1.11 (2018-01-24)

- Modernize setuptools usage. [Leo Singer]

- Drop support for Python 2.6, 3.2, and 3.3. [Leo Singer]

## 0.1.10 (2017-01-05)

- Convert command line interface from optparse to argparse. [Leo Singer]

- Add support for Python 3.5 and drop Python 2.6 and 3.1. [Leo Singer]

## 0.1.9 (2016-07-31)

- Add AMON_ICECUBE_EHE notice type. [Leo Singer]

## 0.1.8 (2016-04-27)

- Add AMON and CALET notice types. [Leo Singer]

## 0.1.7 (2015-09-13)

- Cleanly shut down server socket. [Leo Singer]

  This decreases or eliminates the prevalence of `Address already in use`
  errors when the server is killed (e.g. via a `KeyboardInterrupt`) and
  immediately restarted.

- Add some log messages. [Leo Singer]

- Update setuptools bootstrap script. [Leo Singer]

## 0.1.6 (2015-03-26)

- Update setuptools bootstrap script. [Leo Singer]

## 0.1.5 (2015-03-26)

- Add LIGO/Virgo notice types. [Leo Singer]

## 0.1.4 (2014-05-19)

- Restore compatibility with Python 2.7.3. [Leo Singer]

  Python 2.7.3's io.BytesIO() cannot accept a bytes object, but not a
  buffer object.

## 0.1.3 (2014-05-19)

- Support Python 3.x. [Leo Singer]

- Conditionally import xml.parsers.expat.ExpatError. [Leo Singer]

  Restores compatibility with Python 2.6, which does not have
  xml.etree.cElementTree.ParseError.

- Add unit test for connection closed by server. [Leo Singer]

- Recover from connection closed by peer while reading. [Leo Singer]

- Add nose-based unit tests. Build now uses setuptools. [Leo Singer]

- Fix typos. [Leo Singer]

## 0.1.2 (2014-02-27)

- Print error and recover if VOEvent message has no ivorn. [Leo Singer]

- Recover from malformed XML packets. [Leo Singer]

  If a malformed XML packet is received, log its base64-encoded content
  for debugging purposes and then reconnect.

- Add rudimentary server. [Leo Singer]

- Fix spelling error. [Leo Singer]

## 0.1.1 (2014-02-12)

- Fix Python 2.6 compatibility. [Leo Singer]

- Prefer lxml.etree over xml.etree. [Leo Singer]

  It's faster.

## 0.1 (2014-02-07)

- First release. [Leo Singer]
