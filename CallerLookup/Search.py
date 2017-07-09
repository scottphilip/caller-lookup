# Author:       Scott Philip (sp@scottphilip.com)
# Version:      0.1 (10 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup.Utils import *
from CallerLookup.Strings import *
from GoogleToken import GoogleTokenGenerator
from GoogleToken.Configuration import GoogleTokenConfiguration
from json import dumps, loads
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

HTTP_HEADERS = {"Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US",
                "Accept-Encoding": "gzip",
                "Connection": "Keep-Alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0",
                "Host": "www.truecaller.com",
                "Referer": "https://www.truecaller.com/"}


def get_search_response_data(config, http, number_data):
    auth_token = get_auth_token(config, http)
    query = {CallerLookupKeys.KEY_TYPE: CallerLookupKeys.KEY_TYPE_VALUE,
             CallerLookupKeys.KEY_COUNTRY_CODE: number_data[CallerLookupLabel.REGION],
             CallerLookupKeys.KEY_Q: number_data[CallerLookupLabel.NUMBER_NATIONAL]}
    url = CallerLookupKeys.URL_SEARCH + urlencode(query)
    headers = HTTP_HEADERS
    headers.update({"Authorization": "Bearer {0}".format(auth_token)})
    res_code, res_headers, res_data = http.get(url, headers)
    if res_code is not 200:
        raise Exception(CallerLookupErrors.INVALID_RESPONSE_CODE)
    return loads(res_data)


def get_auth_token(config, http):
    auth_token = get_cached_token(config)
    if auth_token is None:
        google_token = get_google_token(config)
        request_data = {CallerLookupKeys.KEY_ACCESS_TOKEN: google_token}
        # request_headers = {CallerLookupKeys.HTTP_HEADER_CONTENT_TYPE: CallerLookupKeys.HTTP_HEADER_APP_JSON,
        #                   CallerLookupKeys.HTTP_HEADER_REFERER: CallerLookupKeys.URL_REFERER,
        #                   CallerLookupKeys.HTTP_HEADER_ORIGIN: CallerLookupKeys.URL_REFERER}
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
    return auth_token


def get_google_token(config):
    return GoogleTokenGenerator(
        params=config,
        config=GoogleTokenConfiguration(
            phantomjs_path=config.phantomjs_path,
            phantomjs_log_path=config.phantomjs_log_path)) \
        .generate()
