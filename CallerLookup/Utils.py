# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (13 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
import uuid
from configparser import ConfigParser
from datetime import datetime, timedelta
from json import dumps, loads
from os.path import isfile
from os.path import join
import requests
import requests.adapters
import requests.packages.urllib3
from CallerLookup.CountryCodes import CallerLookupCountryCodes
from CallerLookup.Strings import CallerLookupLabel, CallerLookupKeys

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs


def format_number(phone_number, trunk_int_dial_code=None, trunk_country_code=None):
    from phonenumbers import parse, is_valid_number, format_number, PhoneNumberFormat, region_code_for_number, \
        UNKNOWN_REGION
    o = None

    result = {CallerLookupLabel.IS_VALID: False}
    region = trunk_country_code.upper() if trunk_country_code is not None else None
    int_dial_code = trunk_int_dial_code

    if region is None and int_dial_code is not None:
        country_data = CallerLookupCountryCodes.get_country_data(country_int_dial_code=int_dial_code)
        for country in country_data:
            region = country[CallerLookupLabel.COUNTRY_CODE].upper()
            o = parse(phone_number, region)
            break
    else:
        o = parse(phone_number, UNKNOWN_REGION)
    result[CallerLookupLabel.IS_VALID] = is_valid_number(o)
    if result[CallerLookupLabel.IS_VALID]:
        result[CallerLookupLabel.NUMBER_E164] = format_number(o, PhoneNumberFormat.E164)
        result[CallerLookupLabel.NUMBER_NATIONAL] = format_number(o, PhoneNumberFormat.NATIONAL)
        result[CallerLookupLabel.REGION] = region_code_for_number(o)
        result[CallerLookupLabel.REGION_DIAL_CODE] = o.country_code
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


def get_cached_token(config):
    items = get_config(config.cache_path,
                       config.account_email.upper(),
                       [CallerLookupLabel.ACCESS_TOKEN_EXPIRY, CallerLookupLabel.ACCESS_TOKEN])
    if len(items) == 2:
        if datetime.strptime(items[0], "%Y-%m-%d %H:%M:%S") > datetime.utcnow():
            return items[1]
    return None


def get_config(config_path, category, items):
    config = ConfigParser()
    config.read(config_path)
    results = []
    if category in config:
        for item in items:
            if item in config[category]:
                results.append(config[category][item])
    return results


def set_config(config_path, category, items):
    config = ConfigParser()
    config.read(config_path)
    if category not in config:
        config.add_section(category)
    for item in items:
        config[category][item[0]] = item[1]
    with open(config_path, "w") as file:
        config.write(file)


def get_cached_response(config, phone_number):
    import re
    phone_number = re.sub("\D", "", phone_number)
    file_path = join(config.cache_folder_path, phone_number)
    if isfile(file_path):
        with open(file_path) as file:
            result = file.read()
            if result is not None and len(result) > 0:
                return loads(result)
    return None


def set_cached_response(config, phone_number, data):
    import re
    phone_number = re.sub("\D", "", phone_number)
    file_path = join(config.cache_folder_path, phone_number)
    with open(file_path, "w") as file:
        file.write(dumps(data))
    return None


def set_cached_token(config, auth_token):
    expiry = (datetime.utcnow() + timedelta(seconds=3600)).strftime("%Y-%m-%d %H:%M:%S")
    set_config(config.cache_path, config.account_email.upper(),
               [(CallerLookupLabel.ACCESS_TOKEN, auth_token),
                (CallerLookupLabel.ACCESS_TOKEN_EXPIRY, expiry)])


def get_machine_id():
    return str(uuid.getnode())


def encrypt(plain_text):
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    try:
        bytes_text = bytes(plain_text, encoding=CallerLookupKeys.UTF8)
    except:
        bytes_text = bytes(plain_text)
    return cipher_suite.encrypt(bytes_text)


def decrypt(encrypted_text):
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_text).decode(CallerLookupKeys.UTF8)


class CallerLookupReport(object):
    @staticmethod
    def record(number, region, int_dial_code, result, time_taken):
        pass

    @staticmethod
    def get_report_body(number, region, int_dial_code, result, time_taken):
        body_template = "<html><body><h3>{0}</h3><table>{1}</table></body></html>"
        row_template = "<tr><td><b>{0}</b></td><td>{1}</td></tr>"
        rows = row_template.format("DATETIME", datetime.utcnow().strftime("%c") + " (UTC)")
        if region is not None:
            rows += row_template.format("TRUNK_REGION", region)
        if int_dial_code is not None:
            rows += row_template.format("TRUNK_INT_DIAL_CODE", int_dial_code)
        for key in result:
            rows += row_template.format(key, result[key])
        rows += row_template.format("TIME_TAKEN", time_taken)
        return body_template.format(number, row_template)


class CallerLookupHttp(object):
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()

    def get(self, url, headers):
        response = self.session.get(url, headers=headers)
        if self.config.is_debug:
            log_debug(self.config,
                      {
                          "REQUEST": {"URL": url, "HEADERS": str(headers)},
                          "RESPONSE": {"STATUS_CODE": response.status_code,
                                       "HEADERS": str(response.headers), "DATA": response.text}
                      })
        return response.status_code, response.headers, response.text

    def post(self, url, headers, data):
        try:
            encoded_data = bytes(data)
        except:
            encoded_data = bytes(data, encoding=CallerLookupKeys.UTF8)
        headers.update({CallerLookupKeys.HTTP_HEADER_CONTENT_LENGTH: str(len(encoded_data))})
        response = self.session.post(url, headers=headers, data=encoded_data)
        if self.config.is_debug:
            log_debug(self.config,
                      {
                          "REQUEST": {"URL": url, "HEADERS": str(headers), "DATA": encoded_data},
                          "RESPONSE": {"STATUS_CODE": response.status_code,
                                       "HEADERS": str(response.headers), "DATA": response.text}
                      })
        return response.status_code, response.headers, response.text
