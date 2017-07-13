# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (13 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)


class CallerLookupLabel:
    RESULT = "RESULT"
    NUMBER = "NUMBER"
    REGION = "REGION"
    ADDRESS = "ADDRESS"
    MESSAGE = "MESSAGE"
    NAME = "NAME"
    NUMBER_E164 = "NUMBER_E164"
    NUMBER_NATIONAL = "NUMBER_NATIONAL"
    REGION_DIAL_CODE = "REGION_DIAL_CODE"
    SCORE = "SCORE"
    TIME_TAKEN = "TIME_TAKEN"
    COUNTRY_CODE = "COUNTRY_CODE"
    IS_VALID = "IS_VALID"
    COUNTRY_INT_DIAL_CODE = "COUNTRY_INT_DIAL_CODE"
    SUCCESS = "SUCCESS"
    INVALID_NUMBER = "INVALID_NUMBER"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"
    ACCESS_TOKEN = "ACCESS_TOKEN"
    ACCESS_TOKEN_EXPIRY = "ACCESS_TOKEN_EXPIRY"


class CallerLookupErrors:
    COUNTRY_NOT_FOUND = "COUNTRY_NOT_FOUND"
    INVALID_COUNTRY_DATA = "INVALID_COUNTRY_DATA"
    INVALID_RESPONSE_CODE = "INVALID_RESPONSE_CODE"
    ACCESS_TOKEN_NOT_FOUND = "ACCESS_TOKEN_NOT_FOUND"


class CallerLookupKeys(object):
    URL_SEARCH = "http://www.truecaller.com/api/search?"
    URL_TOKEN = "https://www.truecaller.com/api/auth/google?clientId=4"
    OAUTH2_CLIENT_ID = "1051333251514-p0jdvav4228ebsu820jd3l3cqc7off2g.apps.googleusercontent.com"
    OAUTH2_REDIRECT_URI = "https://www.truecaller.com/auth/google/callback"
    OAUTH2_SCOPE = "https://www.googleapis.com/auth/userinfo.email " \
                   "https://www.googleapis.com/auth/userinfo.profile " \
                   "https://www.google.com/m8/feeds/"
    GET_TOKEN_JAVASCRIPT = "localStorage.getItem('tcToken')"
    KEY_TYPE = "type"
    KEY_TYPE_VALUE = "4"
    KEY_COUNTRY_CODE = "countryCode"
    KEY_Q = "q"
    KEY_DATA = "data"
    KEY_SCORE = "score"
    KEY_ADDRESSES = "addresses"
    KEY_ADDRESS = "address"
    KEY_PHONES = "phones"
    KEY_E164_FORMAT = "e164format"
    KEY_NATIONAL_FORMAT = "nationalFormat"
    KEY_DIALLING_CODE = "diallingCode"
    KEY_ACCESS_TOKEN = "accessToken"
    KEY_NAME = "name"
    HTTP_HEADER_CONTENT_ENCODING = "Content-Encoding"
    HTTP_HEADER_CONTENT_TYPE = "content-type"
    HTTP_HEADER_CONTENT_LENGTH = "content-length"
    UTF8 = "utf-8"
    HTTP_HEADER_APP_JSON = "application/json"
    HTTP_HEADER_REFERER = "referer"
    HTTP_HEADER_ORIGIN = "origin"
