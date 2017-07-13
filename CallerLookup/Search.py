# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (13 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
import GoogleToken

from CallerLookup.Utils import *
from CallerLookup.Strings import *
from json import dumps, loads
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

HTTP_HEADERS = {
    "Accept-Encoding": "gzip",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0",
}


def get_search_response_data(config, number_data):
    auth_token = get_auth_token(config)
    query = {CallerLookupKeys.KEY_TYPE: CallerLookupKeys.KEY_TYPE_VALUE,
             CallerLookupKeys.KEY_COUNTRY_CODE: number_data[CallerLookupLabel.REGION],
             CallerLookupKeys.KEY_Q: number_data[CallerLookupLabel.NUMBER_NATIONAL]}
    headers = HTTP_HEADERS
    headers.update({"Authorization": "Bearer {0}".format(auth_token)})
    http = CallerLookupHttp(config)
    res_code, res_headers, res_data = http.get(CallerLookupKeys.URL_SEARCH + urlencode(query), headers)
    if res_code is not 200:
        raise Exception(CallerLookupErrors.INVALID_RESPONSE_CODE)
    return loads(res_data)


def get_auth_token(config):
    auth_token = get_cached_token(config)
    if auth_token is None:
        google_token = get_google_token(config)
        request_data = {CallerLookupKeys.KEY_ACCESS_TOKEN: google_token}
        http = CallerLookupHttp(config)
        (code, headers, data) = http.post(CallerLookupKeys.URL_TOKEN,
                                          headers=HTTP_HEADERS,
                                          data=dumps(request_data))
        if code is not 200:
            raise Exception(CallerLookupErrors.INVALID_RESPONSE_CODE, code)
        token_obj = loads(data)
        if CallerLookupKeys.KEY_ACCESS_TOKEN not in token_obj:
            raise Exception(CallerLookupErrors.ACCESS_TOKEN_NOT_FOUND)
        auth_token = token_obj[CallerLookupKeys.KEY_ACCESS_TOKEN]
        set_cached_token(config, auth_token)
    log_debug(config, "AUTH_TOKEN", auth_token)
    return str(auth_token)


def get_google_token(config):
    token, expiry = GoogleToken.GoogleTokenGenerator(config).generate()
    return token

