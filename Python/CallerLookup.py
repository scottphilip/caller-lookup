#!/usr/bin/python3
#
# Author:       Scott Philip (sp@scottphilip.com)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
#               CallerLookup Copyright (C) 2017 SCOTT PHILIP
#               This program comes with ABSOLUTELY NO WARRANTY
#               This is free software, and you are welcome to redistribute it
#               under certain conditions
#               https://github.com/scottphilip/caller-lookup/blob/master/LICENSE.md
#
import sys

import requests.packages.idna

assert sys.version_info >= (3, 0, 0)

import collections
import argparse
import configparser
import gzip
import http.cookiejar
import json
import phonenumbers
import requests.cookies
import urllib.parse
import urllib.request
import ntpath
import datetime
import logging
import os
import time
import urllib
import urllib.parse

import pyotp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class CallerLookup(object):

    class Parameters(object):
        setting_path = "/var/lib/CallerLookup/CallerLookup.ini"
        cookies_path = "/var/lib/CallerLookup/CallerLookup.cookies"
        country_data_path = "/var/lib/CallerLookup/CountryCodes.json"
        log_path = "/tmp/CallerLookup/CallerLookup.log"
        is_debug = False
        username = None
        password = None
        otp_secret = None

        def __init__(self, dict_values=None):
            if not dict_values is None:
                for key in dict_values:
                    if not dict_values[key] is None:
                        setattr(self, key, dict_values[key])

        def set_root_path(self, path):
            self.setting_path = os.path.join(path, ntpath.basename(self.setting_path))
            self.cookies_path = os.path.join(path, ntpath.basename(self.cookies_path))
            self.country_data_path = os.path.join(path, ntpath.basename(self.country_data_path))
            self.log_path = os.path.join(path, ntpath.basename(self.log_path))

    class Constants(object):

        USER_AGENT = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 "
                      "Firefox/25.0")
        DEFAULT_HEADERS = {"Accept": "application/json, text/plain, */*",
                           "Accept-Language": "en-US",
                           "Accept-Encoding": "gzip",
                           "Connection": "Keep-Alive",
                           "User-Agent": USER_AGENT}
        URL_SEARCH = "https://www.truecaller.com/api/search?"
        URL_TOKEN = "https://www.truecaller.com/api/auth/google?clientId=4"
        URL_TOKEN_CALLBACK = "https://www.truecaller.com/auth/google/callback"
        URL_GOOGLE_ACCOUNTS = "https://accounts.google.com"
        URL_GOOGLE_MYACCOUNT = "https://myaccount.google.com"
        URL_GOOGLE_ACCOUNTS_SERVICELOGIN = "{0}/ServiceLogin".format(URL_GOOGLE_ACCOUNTS)
        URL_GOOGLE_ACCOUNTS_NOFORM = "{0}/x".format(URL_GOOGLE_ACCOUNTS)
        MIN_TIMEOUT = 30

        class OAuth2(object):
            PROTOCOL = "https"
            DOMAIN = "accounts.google.com"
            PATH = "/o/oauth2/v2/auth"
            DATA = {"response_type": "token",
                    "client_id": "1051333251514-p0jdvav4228ebsu820jd3l3cqc7off2g.apps.googleusercontent.com",
                    "redirect_uri": "https://www.truecaller.com/auth/google/callback",
                    "scope": "https://www.googleapis.com/auth/userinfo.email "
                             "https://www.googleapis.com/auth/userinfo.profile "
                             "https://www.google.com/m8/feeds/"}

    Generator = None

    def __init__(self, caller_lookup_parameters=None, dict_parameters=None):
        if caller_lookup_parameters is None:
            caller_lookup_parameters = CallerLookup.Parameters(dict_parameters)
        self.settings = caller_lookup_parameters
        global log_helper
        if log_helper is None:
            log_helper = LogHelper(self.settings)
        log_helper.debug_line_break()
        self.generator = TokenGenerator(self.settings)

    def format_phone_number(self, format_number, format_region):
        format_valid = False
        try:
            if not format_number.startswith("+") \
                    and not format_number.startswith("0"):
                format_number = "+" + format_number

            phone_number = phonenumbers.parse(format_number, format_region.upper())
            format_region = self.get_phone_number_region(str(phone_number.country_code), format_region).upper()
            format_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            format_valid = phonenumbers.is_valid_number(phone_number)

        except:
            ignore = True
        return format_valid, format_number, format_region

    def get_phone_number_region(self, country_dial_code, provided_region):
        try:
            country_data = json.loads(open(self.settings.country_data_path).read())
            for country in country_data:
                if country["CC"] == country_dial_code:
                    return country["CCN"]
        except Exception as e:
            log_helper.error("PHONENUMBER", "REGION", "Error Loading Country Code Data: {0}".format(str(e)))
        return provided_region

    def get_response_invalid(self, number, region):
        return {"result": "invalid_number",
                "number": number,
                "region": region}

    def get_response_error(self, message):
        return {"result": "error",
                "message": message}

    def search(self, phone_number, default_region):
        start_time = time.time()
        (is_valid_number, phone_number, default_region) = \
            self.format_phone_number(phone_number, default_region)
        if not is_valid_number:
            log_helper.info("SEARCH", "Invalid Number", "{0} [{1}]".format(phone_number,
                                                                           default_region))
            return self.get_response_invalid(phone_number, default_region)
        log_helper.info("SEARCH", "Phone Number", "{0} [{1}]".format(phone_number,
                                                                     default_region))
        with HttpHandler(self.settings) as handler:
            query = CallerLookup.Constants.URL_SEARCH + \
                    urllib.parse.urlencode({"type": "4",
                                            "countryCode": str(default_region),
                                            "q": str(phone_number)})
            try:
                (res_code, res_data, res_header) = self \
                    .execute_search(handler, query, False)
            except:
                (res_code, res_data, res_header) = self \
                    .execute_search(handler, query, True)
        return self.format_result(start_time, phone_number, default_region, res_data)

    def format_result(self, start_time, phone_number, default_region, response_data):
        result = {"result": "unknown",
                  "number": phone_number,
                  "region": default_region,
                  "score": 100}

        data = json.loads(response_data)

        if "data" in data:
            data = data["data"]

        if len(data) > 0:
            data = data[0]

        if "score" in data:
            result["score"] = round(data["score"] * 100)

        if "addresses" in data:
            addresses = data["addresses"]
            if len(addresses) > 0:
                if "countryCode" in addresses[0]:
                    result["region"] = addresses[0]["countryCode"].upper()
                if "address" in addresses[0]:
                    result["address"] = addresses[0]["address"]

        if "phones" in data:
            phones = data["phones"]
            if len(phones) > 0:
                if "e164Format" in phones[0]:
                    result["number_e164"] = phones[0]["e164Format"]
                if "nationalFormat" in phones[0]:
                    result["number_national"] = phones[0]["nationalFormat"]
                if "dialingCode" in phones[0]:
                    result["region_dial_code"] = phones[0]["dialingCode"]

        if "name" in data:
            result["name"] = data["name"]
            result["result"] = "success"

        if self.settings.is_debug:
            elapsed = time.time() - start_time
            result["time_taken"] = round(elapsed, 5)

        log_helper.info("SEARCH", "RESULT", "{0}".format(str(result)))
        return result

    def execute_search(self, handler, query, is_retry=False):
        token = self.generator.token(handler, is_retry)
        (response_code, response_data, response_headers) = handler.http_get(query, [
            ("Authorization", "Bearer {0}".format(token)),
            ("Host", "www.truecaller.com"),
            ("Referer", "https://www.truecaller.com/")])
        if response_code != 200:
            raise Exception("Invalid status Code.")
        return (response_code, response_data, response_headers)


class TokenGenerator(object):
    def __init__(self, settings):
        self.settings = settings
        self.load_credentials()

    def load_credentials(self):
        if self.settings.username is None:
            self.settings.username = SettingHelper \
                .get_setting(self.settings.setting_path, "Credentials", "username")
            self.settings.password = SettingHelper \
                .get_setting(self.settings.setting_path, "Credentials", "password")
            self.settings.otp_secret = SettingHelper \
                .get_setting(self.settings.setting_path, "Credentials", "otp_secret")

    def token(self, handler, ignore_cache=False):
        if not ignore_cache:
            cache_date = SettingHelper.get_setting(self.settings.setting_path, "Cache", "TokenExpiry")
            if cache_date is not None and datetime.datetime.strptime(cache_date, "%Y-%m-%d %H:%M:%S") \
                    > datetime.datetime.now():
                token = SettingHelper.get_setting(self.settings.setting_path, "Cache", "Token")
                log_helper.debug("Cached Token: " + token)
                return token
        return self.get_new_token(handler)

    def get_oauth_url(self):
        return "{0}://{1}{2}?{3}" \
            .format(CallerLookup.Constants.OAuth2.PROTOCOL,
                    CallerLookup.Constants.OAuth2.DOMAIN,
                    CallerLookup.Constants.OAuth2.PATH,
                    urllib.parse.urlencode(CallerLookup.Constants.OAuth2.DATA))

    def get_new_token(self, handler):
        token = self.get_refreshed_token(handler)
        if token is None:
            token = self.get_restart_token(handler)
        if token is None:
            raise Exception("Failed to create new token")

        if token.startswith('"') and token.endswith('"'):
            token = token[1:-1]
        log_helper.debug("Saving Token to Cache")

        expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
        SettingHelper.set_setting(self.settings.setting_path, "Cache", "TokenExpiry",
                                  expiry.strftime("%Y-%m-%d %H:%M:%S"))
        SettingHelper.set_setting(self.settings.setting_path, "Cache", "Token", token)

        return token

    def get_refreshed_token(self, handler):
        url = self.get_oauth_url()
        (oauth_res_code, oauth_res_data, oauth_res_header) = handler.http_get(url)
        if oauth_res_code != 302 or not "location" in oauth_res_header:
            return None
        redirect_location = oauth_res_header["location"]
        log_helper.debug("REFRESH TOKEN", "Redirect Url", redirect_location)
        if redirect_location.count(CallerLookup.Constants.URL_GOOGLE_ACCOUNTS) > 0:
            return None
        if redirect_location.count("#") == 0:
            return None
        query_string_data = redirect_location.split("#")[1]
        log_helper.debug("REFRESH TOKEN", "Querystring Data", query_string_data)
        oauth_data = urllib.parse.parse_qs(query_string_data)
        oauth_token = oauth_data["access_token"][0]
        log_helper.debug("REFRESH TOKEN", "Oauth Token", oauth_token)
        request_data = '{"accessToken":"' + oauth_token + '"}'
        handler.http_get(redirect_location, None)
        (token_res_code, token_res_data, token_res_header) = handler \
            .http_post(CallerLookup.Constants.URL_TOKEN, request_data, {"content-type": "application/json",
                                                                        "referer": "https://www.truecaller.com/auth/google/callback",
                                                                        "origin": "https://www.truecaller.com"})
        if token_res_code != 200:
            return None
        refreshed_token = json.loads(token_res_data.encode("utf-8"))
        if not "accessToken" in refreshed_token:
            return None
        refreshed_access_token = refreshed_token["accessToken"]
        log_helper.debug("REFRESH TOKEN", "Success", refreshed_access_token)
        return refreshed_access_token

    def get_restart_token(self, handler):
        service_login = GoogleServiceLogin(self.settings.log_path, self.settings.is_debug)
        try:
            result = service_login.login(self.settings.username,
                                         self.settings.password,
                                         self.settings.otp_secret,
                                         CallerLookup.Constants.OAuth2,
                                         "localStorage.getItem('tcToken')")
            handler.set_cookies(service_login.get_token_cookies())
            return result
        except:
            if self.settings.is_debug:
                raise
            return None


class GoogleServiceLogin(object):

    def __init__(self, log_path, is_debug):
        self.log_path = log_path
        self.root_path = os.path.dirname(self.log_path)
        self.is_debug = is_debug
        if len(self.root_path) > 0:
            if not os.path.exists(self.root_path):
                os.makedirs(self.root_path)
        self.driver = webdriver \
            .PhantomJS(desired_capabilities={
            "phantomjs.page.settings.userAgent": CallerLookup.Constants.USER_AGENT})

    @staticmethod
    def wait_for(condition_function, timeout):
        start_time = time.time()
        while time.time() < start_time + timeout:
            if condition_function():
                return True
            else:
                time.sleep(0.5)
        return False

    def get_token_cookies(self, url=None):
        if url is None:
            url = CallerLookup.Constants.URL_GOOGLE_ACCOUNTS_NOFORM
        self.driver.get(url)
        return self.driver.get_cookies()

    def set_token_cookies(self, cookies):
        self.driver.get(CallerLookup.Constants.URL_GOOGLE_ACCOUNTS_NOFORM)
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except:
                ignore = True

    def save_screenshot(self, index, name, stage="1"):
        if self.is_debug:
            file_name = "{0}-{1}_{2}_{3}.png".format(str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")),
                                                     index, name, stage)
            folder_path = os.path.join(self.root_path, "Screenshots")
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            full_path = os.path.join(folder_path, file_name)
            self.driver.get_screenshot_as_file(full_path)
            log_helper.debug("LOGIN", "SCREENSHOT", "URL={0} File={1}".format(self.driver.current_url, full_path))

    def open_login_page(self):
        self.driver.get(self.get_oauth2_url())
        self.save_screenshot(1, "LoginPage")

    def enter_email(self):
        self.save_screenshot(2, "Email", "1")
        WebDriverWait(self.driver, CallerLookup.Constants.MIN_TIMEOUT).until(ec.element_to_be_clickable((By.ID, "Email")))
        self.driver.find_element_by_id("Email").send_keys(self.username)
        WebDriverWait(self.driver, CallerLookup.Constants.MIN_TIMEOUT).until(ec.element_to_be_clickable((By.ID, "next")))
        self.driver.find_element_by_id("next").click()
        self.save_screenshot(2, "Email", "2")

    def enter_password(self):
        self.save_screenshot(3, "Password", "1")
        WebDriverWait(self.driver, CallerLookup.Constants.MIN_TIMEOUT).until(ec.element_to_be_clickable((By.ID, "Passwd")))
        self.driver.find_element_by_id("Passwd").send_keys(self.password)
        WebDriverWait(self.driver, CallerLookup.Constants.MIN_TIMEOUT).until(ec.element_to_be_clickable((By.ID, "signIn")))
        self.driver.find_element_by_id("signIn").click()
        self.save_screenshot(3, "Password", "2")

    def dual_factor(self):
        if self.driver.current_url.find("/challenge/totp") > 0:
            return self.enter_totp()
        elif self.driver.current_url.count("/challenge/az") > 0:
            return self.wait_for(self.is_login_complete, 300)
        return True

    def enter_totp(self):
        self.save_screenshot(4, "TOTP", "1")
        if self.otp_secret is None:
            raise Exception("Sign in requires Two Step authentication but TOTP Secret has not been set.")
        code = pyotp.TOTP(self.otp_secret).now()
        WebDriverWait(self.driver, CallerLookup.Constants.MIN_TIMEOUT).until(ec.element_to_be_clickable((By.ID, "totpPin")))
        self.driver.find_element_by_id("totpPin").send_keys(code)
        self.driver.find_element_by_id("submit").click()
        self.save_screenshot(4, "TOTP", "2")
        return True

    def get_oauth2_url(self):
        return "{0}://{1}{2}?{3}" \
            .format(CallerLookup.Constants.OAuth2.PROTOCOL,
                    CallerLookup.Constants.OAuth2.DOMAIN,
                    CallerLookup.Constants.OAuth2.PATH,
                    urllib.parse.urlencode(CallerLookup.Constants.OAuth2.DATA))

    def login(self, username, password, otp_secret, oauth2, return_script):
        self.username = username
        self.password = password
        self.otp_secret = otp_secret
        self.oauth2 = oauth2
        self.return_script = return_script
        self.open_login_page()
        self.enter_email()
        self.enter_password()
        if not self.dual_factor():
            raise Exception("Dual Factor Login Error.")
        if not self.wait_login_complete():
            raise Exception("Unable to confirm successful login")
        return self.get_result_data()

    def wait_login_complete(self):
        return self.wait_for(self.is_login_complete, CallerLookup.Constants.MIN_TIMEOUT)

    def is_login_complete(self):
        return self.driver.execute_script("return {0} != null".format(self.return_script))

    def get_result_data(self):
        return self.driver.execute_script("return {0}".format(self.return_script))


class HttpHandler(object):
    class NoRedirect(urllib.request.HTTPErrorProcessor):
        def http_response(self, request, response):
            return response

        https_response = http_response

    def __init__(self, settings):
        self.settings = settings
        self.init_cookies()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_cookies()

    @staticmethod
    def get_headers(append_headers=None, include_default=True):
        result = {}
        if append_headers is not None:
            result.update(append_headers)
        if include_default:
            result.update(CallerLookup.Constants.DEFAULT_HEADERS)
        return result

    def http_get(self, url, headers=None, include_default_headers=True):
        return self._http_request("GET", url, None, headers, include_default_headers)

    def http_post(self, url, data, headers=None, include_default_headers=True):
        return self._http_request("POST", url, data, headers, include_default_headers)

    def _http_request(self, method, url, data=None, headers=None, include_default_headers=True):

        log_helper.debug(method, "REQUEST", "URL={0}".format(url))

        add_headers = self.get_headers(headers, include_default_headers)
        encoded_data = None
        if not data is None:
            encoded_data = bytes(data, "utf-8")
            add_headers.update({"content-length": len(encoded_data)})

        request = urllib.request.Request(url, data=encoded_data, headers=add_headers, method=method)

        if data is not None:
            log_helper.debug(method, "REQUEST", "DATA={0}".format(str(data)))

        try:
            response = self._opener.open(request)
        finally:
            log_helper.debug(method, "REQUEST", "HEADERS={0}".format(json.dumps(request.header_items())))

        response_code = response.getcode()
        log_helper.debug(method, "RESPONSE", "STATUS_CODE={0}".format(response_code))
        response_headers = response.info()
        result_dict = collections.defaultdict(list)
        for key, value in response_headers.items():
            result_dict[key].append(value)
        log_helper.debug(method, "RESPONSE", "HEADERS={0}".format(json.dumps(result_dict)))
        if response_headers.get('Content-Encoding') == 'gzip':
            response_data = gzip.GzipFile(fileobj=response).read().decode("utf-8")
        else:
            response_data = response.read().decode("utf-8")
        log_helper.debug(method, "RESPONSE", "DATA={0}".format(response_data))

        return response_code, response_data, response_headers

    def init_cookies(self):
        self._cookiejar = http.cookiejar.MozillaCookieJar()
        if os.path.isfile(self.settings.cookies_path):
            self._cookiejar.load(self.settings.cookies_path, ignore_discard=True)
        self._opener = urllib.request.build_opener(HttpHandler.NoRedirect,
                                                   urllib.request.HTTPCookieProcessor(self._cookiejar))

    def get_cookies(self, full_url):
        url = urllib.parse.urlparse(full_url)
        domain = url.netloc
        request_jar = requests.cookies.RequestsCookieJar()
        request_jar.update(self._cookiejar)
        return request_jar.get_dict(domain)

    def is_cookie_available(self, full_url):
        return len(self.get_cookies(full_url)) > 0

    def reset_cookies(self):
        self._cookiejar.clear()
        self.save_cookies()
        self.init_cookies()

    def set_cookies(self, cookies):
        for c in cookies:
            self._cookiejar.set_cookie(self._get_cookie(c))
        self.save_cookies()

    def save_cookies(self):
        self._cookiejar.save(self.settings.cookies_path, ignore_discard=True)

    @staticmethod
    def _get_cookie(item):
        if item is None:
            return None
        return http.cookiejar.Cookie(item["version"] if "version" in item else 1,
                                     item["name"] if "name" in item else None,
                                     item["value"] if "value" in item else None,
                                     item["port"] if "port" in item else None,
                                     True if "port" in item else False,
                                     item["domain"] if "domain" in item else None,
                                     True if "domain" in item else False,
                                     True if "domain" in item and item["domain"].startswith(".") in item else False,
                                     item["path"] if "path" in item else None,
                                     True if "path" in item else False,
                                     True if "secure" in item else False,
                                     item["expiry"] if "expiry" in item else None,
                                     True if "discard" in item else False,
                                     item["comment"] if "comment" in item else None,
                                     item["comment_url"] if "comment_url" in item else None,
                                     1, rfc2109=True)


class SettingHelper(object):
    @staticmethod
    def get_setting(setting_path, setting_category, setting_name):
        """Get Application Setting"""
        config = configparser.ConfigParser()
        config.read(setting_path)
        if setting_category in config:
            if setting_name in config[setting_category]:
                return config[setting_category][setting_name]
        return None

    @staticmethod
    def set_setting(setting_path, setting_category, setting_name, setting_value):
        config = configparser.ConfigParser()
        config.read(setting_path)
        if setting_category not in config:
            config.add_section(setting_category)
        config[setting_category][setting_name] = setting_value
        with open(setting_path, 'w') as configfile:
            config.write(configfile)


class LogHelper(object):
    def __init__(self, settings):
        self.settings = settings
        self.path = os.path.dirname(self.settings.log_path)

        if len(self.path) > 0:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        self._log = logging.getLogger("CallerLookup")
        self._log.propagate = False
        handler = logging.FileHandler(self.settings.log_path)
        formatter = logging.Formatter('%(asctime)s   >>   %(levelname)8s   >>   %(message)s')
        handler.setFormatter(formatter)
        self._log.addHandler(handler)
        self._log.setLevel(logging.INFO)

        if self.settings.is_debug:
            self._log.setLevel(logging.DEBUG)

    def debug_line_break(self):
        line_break = ("*******************************************************************"
                      "*****************************************")
        self._log.debug("")
        self._log.debug("")
        self._log.debug(line_break)

    def debug(self, major="", minor="", message=""):
        """Log Debug Message"""
        self._log.debug("{0:20s} {1:30s} {2}".format(major, minor, message))

    def info(self, major="", minor="", message=""):
        """Log Info Message"""
        self._log.info("{0:20s} {1:30s} {2}".format(major, minor, message))

    def warning(self, major="", minor="", message=""):
        """Log Warning Message"""
        self._log.warning("{0:20s} {1:30s} {2}".format(major, minor, message))

    def error(self, major="", minor="", message=""):
        """Log Error Message"""
        self._log.error("{0:20s} {1:30s} {2}".format(major, minor, message))

    def format(self, message):
        if message is not None:
            if hasattr(message, "encode"):
                return message.encode()
        return message


log_helper = None

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Reverse Caller Id',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=("Example: {0} --number +12024561111\n"
                                             "         {0} --number 02079309000 --region gb")
                                     .format(os.path.basename(__file__)))

    parser.add_argument("--number", "--n",
                        nargs="+",
                        dest="phone_numbers",
                        help="Phone number accepted in any standard format. When not in international format, the \
                                  default region parameter must be supplied",
                        action='append', required=True)

    parser.add_argument("--region", "--r",
                        dest="default_region",
                        default="gb",
                        help="The home region that the trunk belongs to.  Only required when phone number" \
                             " is supplied without an international dialling code.  Must be in CCN format.  See" \
                             "CountryCodes.json",
                        required=False)

    parser.add_argument("--path", "--p",
                        help="Working Directory",
                        dest="application_path",
                        required=False)

    parser.add_argument("--settings", "--s",
                        help="Path to Settings INI file",
                        dest="setting_path",
                        required=False)

    parser.add_argument("--cookies", "--c",
                        help="Path to Cookie store file",
                        dest="cookies_path",
                        required=False)

    parser.add_argument("--countrycodes", "--cc",
                        help="Path to Country Codes data file",
                        dest="country_data_path",
                        required=False)

    parser.add_argument("--logpath", "--l",
                        help="Path to Log Directory",
                        dest="log_path",
                        required=False)

    parser.add_argument("--username", "--un",
                        help="Google Account Username",
                        dest="username",
                        required=False)

    parser.add_argument("--password", "--pw",
                        help="Google Account Password",
                        dest="password",
                        required=False)

    parser.add_argument("--otp_secret", "--otp",
                        help="Google Account Two-Factor Auth Secret",
                        dest="otp_secret",
                        required=False)

    parser.add_argument("--debug",
                        help="Debug mode",
                        action="store_true",
                        dest="is_debug")

    args = vars(parser.parse_args())
    params = CallerLookup.Parameters(args)

    if not args["application_path"] is None:
        params.set_root_path(args["application_path"])

    try:

        lookup = CallerLookup(params)

        results = []

        for phone_number in args["phone_numbers"]:
            n = " ".join(phone_number)
            result = lookup.search(n, args["default_region"])
            results.append(result)

        print(json.dumps(results))

        exit(0)

    except Exception as e:

        print(str([{"Result": "Error", "Error": str(e)}]))
        raise
