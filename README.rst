|BuildStatus|

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

    with CallerLookup(account_email="username@gmail.com",
                      account_password="password",
                      account_otp_secret="secret") as caller_lookup:

        result = caller_lookup.search("0202-456-1111", int_dial_code="1")
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

-  Google Token

   -  Github https://github.com/scottphilip/GoogleToken

   -  PyPI https://pypi.python.org/pypi/GoogleToken

-  phonenumbers

   -  Github https://github.com/daviddrysdale/python-phonenumbers

   -  PyPI https://pypi.python.org/pypi/phonenumbers

Credits
-------

Scott Philip

Berlin, Germany

Licence
-------

GNU General Public License (Version 3, 29 June 2007)

CallerLookup Copyright © 2017 Scott Philip

.. |BuildStatus| image:: https://travis-ci.org/scottphilip/caller-lookup.svg?branch=master
:target: https://travis-ci.org/scottphilip/caller-lookup