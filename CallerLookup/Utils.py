# Author:       Scott Philip (sp@scottphilip.com)
# Version:      0.1 (10 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup.CountryCodes import CallerLookupCountryCodes
from CallerLookup.Strings import CallerLookupLabel, CallerLookupErrors, CallerLookupKeys
from configparser import ConfigParser
from os.path import expanduser, join
from datetime import datetime, timedelta
from http.cookiejar import MozillaCookieJar
from os.path import isfile
try:
    from urllib.parse import urlparse, parse_qs
    from urllib.request import build_opener, Request, HTTPCookieProcessor, HTTPErrorProcessor
except ImportError:
    from urlparse import urlparse, parse_qs
    from urllib2 import HTTPCookieProcessor, build_opener, Request, HTTPErrorProcessor


def format_number(phone_number, trunk_int_dial_code=None, country_code=None):
    from phonenumbers import parse, is_valid_number, format_number, PhoneNumberFormat
    result = {CallerLookupLabel.IS_VALID: False}
    country_data = CallerLookupCountryCodes.get_country_data(country_int_dial_code=trunk_int_dial_code,
                                                             country_code=country_code)
    if country_data is None:
        raise Exception(CallerLookupErrors.COUNTRY_NOT_FOUND)
    if CallerLookupLabel.COUNTRY_CODE not in country_data:
        raise Exception(CallerLookupErrors.INVALID_COUNTRY_DATA)
    trunk_region = country_data[CallerLookupLabel.COUNTRY_CODE]
    o = parse(phone_number, trunk_region.upper())
    result[CallerLookupLabel.IS_VALID] = is_valid_number(o)
    if result[CallerLookupLabel.IS_VALID]:
        result[CallerLookupLabel.NUMBER_E164] = format_number(o, PhoneNumberFormat.E164)
        result[CallerLookupLabel.NUMBER_NATIONAL] = format_number(o, PhoneNumberFormat.NATIONAL)
        result[CallerLookupLabel.REGION] = trunk_region
        result[CallerLookupLabel.REGION_DIAL_CODE] = country_data[CallerLookupLabel.COUNTRY_INT_DIAL_CODE]
    return result


def log_debug(config, *args, **kwargs):
    if config is not None and config.logger is not None:
        config.logger.debug(["CALLER_LOOKUP", args], **kwargs)


def log_info(config, *args, **kwargs):
    if config is not None and config.logger is not None:
        config.logger.info(["CALLER_LOOKUP", args], **kwargs)


def log_error(config, *args, **kwargs):
    if config is not None and config.logger is not None:
        config.logger.error(["CALLER_LOOKUP", args], **kwargs)


def get_cookies_path(config):
    if config.cookie_storage_path is not None:
        return config.cookie_storage_path
    return join(expanduser("~"), "{0}.cookies".format(config.account_email))


def get_cache_path(config):
    if config.cache_path is not None:
        return config.cache_path
    return join(expanduser("~"), "CallerLookup.ini")


def get_cached_token(config):
    cache = ConfigParser()
    cache.read(get_cache_path(config))
    if config.account_email.upper() in cache:
        if CallerLookupLabel.ACCESS_TOKEN_EXPIRY in cache[config.account_email.upper()]:
            expiry = cache[config.account_email.upper()][CallerLookupLabel.ACCESS_TOKEN_EXPIRY]
            if expiry is not None and datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S") > datetime.now():
                if CallerLookupLabel.ACCESS_TOKEN in cache[config.account_email.upper()]:
                    return cache[config.account_email.upper()][CallerLookupLabel.ACCESS_TOKEN]
    return None


def set_cached_token(config, auth_token):
    cache = ConfigParser()
    cache.read(get_cache_path(config))
    if config.account_email.upper() not in cache:
        cache.add_section(config.account_email.upper())
    expiry = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    cache[config.account_email.upper()][CallerLookupLabel.ACCESS_TOKEN] = auth_token
    cache[config.account_email.upper()][CallerLookupLabel.ACCESS_TOKEN_EXPIRY] = expiry
    with open(get_cache_path(config), "w") as cache_file:
        cache.write(cache_file)


class HttpHandler(object):
    class NoRedirect(HTTPErrorProcessor):
        def http_response(self, request, response):
            return response
        https_response = http_response


class CallerLookupHttp(object):

    def __init__(self, config):
        self.config = config
        self.cookie_jar = MozillaCookieJar()
        if isfile(get_cookies_path(config)):
            self.cookie_jar.load(get_cookies_path(config))
        self.build_opener = build_opener(HttpHandler.NoRedirect,
                                         HTTPCookieProcessor(self.cookie_jar))

    def save_cookies(self):
        self.cookie_jar.save(get_cookies_path(self.config))

    def get(self, url, headers):
        request = Request(url, headers=headers)
        response = self.build_opener.open(request)
        return self.get_response(response)

    def post(self, url, headers, data):
        try:
            encoded_data = bytes(data)
        except:
            encoded_data = bytes(data, encoding=CallerLookupKeys.UTF8)
        headers.update({CallerLookupKeys.HTTP_HEADER_CONTENT_LENGTH: str(len(encoded_data))})
        request = Request(url, headers=headers, data=encoded_data)
        response = self.build_opener.open(request)
        return self.get_response(response)

    def get_response(self, response):
        code, headers, data = response.getcode(), response.info(), None
        return code, headers, self.decode(
            headers.get(CallerLookupKeys.HTTP_HEADER_CONTENT_ENCODING), response)

    def decode(self, encoding, response):
        if encoding == "gzip":
            result = self.decode_gzip(response)
        else:
            result = self.decode_string(response)
        return result.decode(CallerLookupKeys.UTF8)

    @staticmethod
    def decode_string(response):
        return response.read()

    @staticmethod
    def decode_gzip(response):
        from gzip import GzipFile
        try:
            from StringIO import StringIO
            return GzipFile(fileobj=StringIO(response.read())).read()
        except:
            return GzipFile(fileobj=response).read()


