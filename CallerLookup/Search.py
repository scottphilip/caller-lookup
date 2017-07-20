# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (20 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup.Utils.Logs import *
from CallerLookup.Strings import *
from CallerLookup.Utils.Cache import *
from CallerLookup.Utils.Http import *

from json import dumps, loads

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

HTTP_HEADERS = {
    "Accept-Encoding": "gzip",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0",
}


def run_search(config, number_data):
    attempt = 0
    while True:
        attempt += 1
        try:
            result = get_search_response_data(config, number_data)
            return result
        except Exception as ex:
            if attempt >= 3:
                raise
            log_debug(config, "SEARCH ERROR", {"ATTEMPT": attempt, "ERROR": str(ex)})
            config.clear_cached_token()


def get_search_response_data(config, number_data):
    try:
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
    except Exception as ex:
        config.clear_cached_token()
        import traceback
        log_debug(config, {"SEARCH_DATA_ERROR": {"ERROR": str(ex),
                                                 "STACK": traceback.format_exc()}})
        raise


def get_auth_token(config):
    auth_token = config.get_cached_token()
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
        config.set_cached_token(auth_token)
    log_debug(config, "AUTH_TOKEN", auth_token)
    return str(auth_token)


def get_google_token_config(config):
    account_data = config.settings[config.account]
    from GoogleToken import GoogleTokenConfiguration
    return GoogleTokenConfiguration(account_email=account_data[CallerLookupConfigStrings.USERNAME],
                                    account_password=account_data[CallerLookupConfigStrings.PASSWORD],
                                    account_otp_secret=account_data[CallerLookupConfigStrings.SECRET],
                                    oauth_client_id=CallerLookupKeys.OAUTH2_CLIENT_ID,
                                    oauth_redirect_uri=CallerLookupKeys.OAUTH2_REDIRECT_URI,
                                    oauth_scope=CallerLookupKeys.OAUTH2_SCOPE,
                                    cookie_storage_path=join(config.data_dir, config.account + ".cookies"),
                                    logger=config.logger,
                                    image_path=join(config.log_dir, config.account),
                                    execute_script=CallerLookupKeys.GET_TOKEN_JAVASCRIPT,
                                    phantomjs_path=config.settings[CallerLookupConfigStrings.GENERAL]
                                    [CallerLookupConfigStrings.PHANTOMJS_PATH],
                                    phantomjs_log_path=join(config.log_dir, "phantomjs.log"))


def get_google_token(config):
    from GoogleToken import GoogleTokenGenerator
    token, expiry = GoogleTokenGenerator(get_google_token_config(config)).generate()
    return token
