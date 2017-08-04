.. image:: https://travis-ci.org/scottphilip/caller-lookup.svg?branch=master
   :target: https://travis-ci.org/scottphilip/caller-lookup

.. image:: https://img.shields.io/pypi/v/CallerLookup.svg
   :target: https://pypi.python.org/pypi/CallerLookup

.. image:: https://img.shields.io/pypi/pyversions/CallerLookup.svg
   :target: https://pypi.python.org/pypi/CallerLookup

Caller Lookup
=============

Wrapper for TrueCaller

Installation Instructions
-------------------------

::

    pip install CallerLookup

Usage
-----

.. code:: python

    with CallerLookup(username="username@gmail.com",
                      password="password",
                      secret="secret") as caller_lookup:

        result = caller_lookup.search(number="0202-456-1111", region_dial_code="1")
        print(str(result))

Output:

.. code:: json

    {
        "IS_VALID": True,
        "SCORE": 80.0,
        "RESULT": "SUCCESS",
        "REGION_DIAL_CODE": "1",
        "ADDRESS": "1600PennsylvaniaAveNW,
        TheWhiteHouse,
        Downtown,
        Washington,
        DC20006",
        "NUMBER_E164": "+12024561111",
        "REGION": "US",
        "NUMBER_NATIONAL": "(202)456-1111",
        "TIME_TAKEN": 0.701,
        "NAME": "WhiteHouse"
    }

Dependencies
------------

PyPI Packages:

    -  GoogleToken
    -  phonenumbers
    -  cryptography
    -  appdirs
    -  requests
    -  python-dateutil

Testing
-------

Tested on Python:

    - 2.7
    - 3.6

Credits
-------

Scott Philip

Berlin, Germany

Licence
-------

GNU General Public License (Version 3, 29 June 2007)

CallerLookup Copyright © 2017 Scott Philip
