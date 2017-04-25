#!/usr/bin/python

import argparse
import configparser
import datetime
import json
import logging
import os
import time
import urllib.parse

import phonenumbers
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class ReverseLookup(object):
    """PBX Tools - Reverse Caller Id"""

    Url_Query = 'https://www.truecaller.com/api/search?%s'

    def __init__(self, setting_path, log_path, is_debug):

        global log_helper
        log_helper = self.LogHelper(log_path, is_debug)

        self._Generator = self.TokenGenerator(setting_path)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    @staticmethod
    def _get_headers(token):

        if token.startswith('"') and token.endswith('"'):
            token = token[1:-1]
        return {"Authorization": "Bearer {}".format(token),
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.truecaller.com/",
                "Accept-Language": "en-US",
                "Accept-Encoding": "gzip, deflate",
                "Host": "www.truecaller.com",
                "Connection": "Keep-Alive",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36"
                }

    def _get_data(self, number, region):
        """Get Caller Data"""

        attempt = 1
        is_token_expired = False
        request_headers, result_status_code, result_headers, result_data = None, None, None, None
        url = self.Url_Query % urllib.parse.urlencode({"type": 4, "countryCode": region, "q": number})

        while attempt <= 1:

            token = self._Generator.get_token(is_token_expired)
            attempt = attempt + 1
            if token is None:
                continue

            request_headers = self._get_headers(token)
            log_helper.debug("Query:   " + url)
            log_helper.debug("Headers: " + str(request_headers))

            (result_status_code, result_data,
             result_headers) = self.Utils.http_get(url, request_headers)

            if result_status_code == 200:
                log_helper.debug("Response: {}".format(result_data))
                return json.loads(result_data)
            if result_status_code == 401:
                log_helper.debug("Token {} has expired.".format(token))
                is_token_expired = True
                continue

        result = {"Result": "Fail",
                  "Request": {
                      "URL": url,
                      "Headers": request_headers
                  },
                  "Response": {
                      "Status_Code": result_status_code,
                      "Headers": result_headers,
                      "Body": result_data}
                  }
        log_helper.error(result)
        return result

    @staticmethod
    def get_value(data, setting_name):
        if data is not None:
            if setting_name in data:
                return str(data[setting_name])
        return "Unknown"

    def search(self, number, default_region="DE", country_code_path="CountryCodes.json"):

        def get_ccn(country_dial_code):
            try:
                country_data = json.loads(open(country_code_path).read())
                for country in country_data:
                    if country["CC"] == country_dial_code:
                        return country["CCN"]
                return None
            except Exception as e:
                log_helper.error("Get CCN: " + str(e))
                raise

        def format_phonenumber(format_number, format_region):

            format_valid = False
            try:
                phone_number = phonenumbers.parse(format_number, format_region.upper())
                format_region = get_ccn(str(phone_number.country_code))
                format_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
                format_valid = phonenumbers.is_valid_number(phone_number)
            except:
                ignore = True

            return format_valid, format_number, format_region

        log_helper.info("Search: {} ({})".format(number, default_region))

        result = {"Result": "Unknown",
                  "Number": number,
                  "Region": default_region,
                  "Name": "",
                  "Score": 1}

        try:

            (is_valid_number, number, region) = format_phonenumber(number, default_region)

            if is_valid_number:

                result["Number"] = number
                result["Region"] = region.upper()

                response = self._get_data(number, region)

                if "data" in response:
                    item_count = len(response["data"])
                    if item_count > 0:
                        data = response["data"][0]
                        if data is not None:

                            if "name" in data:
                                result["Name"] = data["name"]
                                result["Result"] = "Success"

                            if "score" in data:
                                result["Score"] = data["score"]
            else:

                result["Result"] = "Invalid"

        except Exception as e:
            result["Result"] = "Error"
            result["Error"] = str(e)

        log_helper.info("Search Result: {}".format(str(result)))

        return result

    class TokenGenerator(object):

        url_servicelogon = "https://accounts.google.com/ServiceLogin"
        url_accounts = "https://accounts.google.com"
        url_myaccount = "https://myaccount.google.com"
        url_gettoken = "{}/o/oauth2/v2/auth?response_type=token&client_id=1051333251514" \
                       "-p0jdvav4228ebsu820jd3l3cqc7off2g.apps.googleusercontent.com&redirect_uri=https://www" \
                       ".truecaller.com/auth/google/callback&scope=https://www.googleapis.com/auth/userinfo.email" \
                       "%20https://www.googleapis.com/auth/userinfo.profile%20https://www.google.com/m8/feeds/ " \
            .format(url_accounts)

        def __init__(self, setting_path):
            self.setting_path = setting_path
            self.username = ReverseLookup.Utils.get_setting(setting_path, "Credentials", "Username")
            self.password = ReverseLookup.Utils.get_setting(setting_path, "Credentials", "Password")

        def validate(self):
            if self.username is None:
                raise Exception("Username setting in %s is unset" % self.setting_path)
            if self.password is None:
                raise Exception("Password setting in %s is unset" % self.setting_path)
            log_helper.debug("Setting Validation Passed")

        def create_token(self, username, password):
            def wait_for(condition_function, timeout):
                start_time = time.time()
                while time.time() < start_time + timeout:
                    if condition_function():
                        return True
                    else:
                        time.sleep(0.1)
                return False

            def is_token_created():
                return driver.execute_script("return localStorage.getItem('tcToken') != null")

            def restore_cookies():
                log_helper.debug("Restoring Cookies...")
                driver.get(self.url_servicelogon)
                log_helper.debug("Navigated URL: {}".format(self.url_servicelogon))
                log_helper.debug("Resulted URL: {}".format(driver.current_url))

                store = ReverseLookup.Utils.get_setting(self.setting_path, "Cache", "Cookies")
                if store is not None:
                    log_helper.debug("Trying to restore cookies...")
                    cookies = json.loads(store)
                    is_set = False
                    if cookies is not None:
                        for cookie in cookies:
                            try:
                                driver.add_cookie(cookie)
                                is_set = True
                            except:
                                ignore = True
                    if is_set:
                        driver.get(self.url_accounts)
                        log_helper.debug("Navigated URL: {}".format(self.url_accounts))
                        log_helper.debug("Resulted URL: {}".format(driver.current_url))

            def save_cookies():
                if driver.current_url.startswith(self.url_myaccount):
                    ReverseLookup.Utils.set_setting(self.setting_path, "Cache", "Cookies",
                                                    json.dumps(driver.get_cookies()))

            def save_screenshot(name):
                if log_helper.is_debug:
                    driver.save_screenshot(os.path.join(log_helper.path,
                                                        '{}-{}.png'
                                                        .format(str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")),
                                                                name)))

            self.validate()
            driver = webdriver.PhantomJS(service_log_path=os.path.join(log_helper.path, "webdriver.log"))

            try:
                delay = 3
                driver.set_window_size(1120, 550)

                restore_cookies()

                if driver.current_url.startswith(self.url_accounts):
                    log_helper.debug("Completing Logon Form")
                    if driver.find_element_by_id('Email') is not None:
                        log_helper.debug("Completing Username")
                        driver.find_element_by_id('Email').send_keys(username)
                        driver.find_element_by_id("next").click()

                    WebDriverWait(driver, delay).until(ec.element_to_be_clickable((By.ID, 'Passwd')))
                    driver.find_element_by_id('Passwd').send_keys(password)
                    driver.find_element_by_id("signIn").click()
                    if driver.current_url.count("challenge") > 0:
                        save_screenshot("Challenge")
                        raise Exception("Account must be logged in manually.  Resulted in user challenge")
                    save_cookies()

                log_helper.debug("Requesting Token...")
                driver.get(self.url_gettoken)
                log_helper.debug("Navigated URL: {}".format(self.url_gettoken))
                log_helper.debug("Resulted URL: {}".format(driver.current_url))

                # noinspection PyTypeChecker
                if wait_for(is_token_created, delay):
                    return driver.execute_script("return localStorage.getItem('tcToken')")
                raise Exception("Timeout")

            except Exception as e:
                log_helper.error(e)
                save_screenshot("Error")
                raise

        def get_token(self, force_update):
            """Get the token to go with each request"""
            if not force_update:

                cache_date = ReverseLookup.Utils.get_setting(self.setting_path, "Cache", "TokenExpiry")
                if cache_date is not None:
                    cached_expiry = datetime.datetime.strptime(cache_date, "%Y-%m-%d %H:%M:%S")
                    if cached_expiry > datetime.datetime.now():
                        token = ReverseLookup.Utils.get_setting(self.setting_path, "Cache", "Token")
                        if token.startswith('"') and token.endswith('"'):
                            token = token[1:-1]
                        log_helper.debug("Cached Token: " + token)
                        return token

            token = self.create_token(self.username, self.password)
            log_helper.debug("Created Token: " + token)

            if token is not None:
                log_helper.debug("Saving Token to Cache")
                expiry = datetime.datetime.now() + datetime.timedelta(hours=6)
                ReverseLookup.Utils.set_setting(self.setting_path, "Cache", "TokenExpiry",
                                                expiry.strftime("%Y-%m-%d %H:%M:%S"))
                ReverseLookup.Utils.set_setting(self.setting_path, "Cache", "Token", token)

            return token

    class Utils(object):
        """PBX Tools Shared Utilities"""

        @staticmethod
        def http_get(url, headers):
            """HTTP Get.  Returns: status_code, content, headers"""
            res = requests.get(url, headers=headers, verify=False, )
            return res.status_code, res.text, res.headers

        @staticmethod
        def http_post(url, headers, data, session):
            """HTTP Get.  Returns: status_code, content, headers"""
            if session is None:
                res = requests.post(url, headers=headers, data=data)
                return res.status_code, res.text, res.headers
            return session.post(url, headers=headers, data=data)

        @staticmethod
        def get_setting(path, setting_category, setting_name):
            """Get Application Setting"""
            config = configparser.ConfigParser()
            config.read(path)
            if setting_category in config:
                if setting_name in config[setting_category]:
                    return config[setting_category][setting_name]
            return None

        @staticmethod
        def set_setting(path, setting_category, setting_name, setting_value):
            config = configparser.ConfigParser()
            config.read(path)
            if setting_category not in config:
                config.add_section(setting_category)
            config[setting_category][setting_name] = setting_value
            with open(path, 'w') as configfile:
                config.write(configfile)

    class LogHelper(object):

        class Flag:
            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            WARNING = '\033[93m'
            FAIL = '\033[91m'
            ENDC = '\033[0m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'

        def __init__(self, path, is_debug=False):
            self.path = path

            self._log = logging.getLogger(__name__)
            handler = logging.FileHandler(os.path.join(path, "CallerLookup.log"))
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            self._log.addHandler(handler)
            self._log.setLevel(logging.INFO)

            self.is_debug = is_debug
            if self.is_debug:
                self._log.setLevel(logging.DEBUG)

        def debug(self, message):
            """Log Debug Message"""
            self._log.debug(message)

        def info(self, message):
            """Log Info Message"""
            self._log.info(message)

        def warning(self, message):
            """Log Warning Message"""
            self._log.warning(message)

        def error(self, message):
            """Log Error Message"""
            self._log.error(message)


log_helper = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reverse Caller Id')

    parser.add_argument("--number",
                        dest="phone_number",
                        help="Phone number accepted in any standard format. When not in international format, the \
                              default region parameter must be supplied",
                        required=True)

    parser.add_argument("--region",
                        dest="default_region",
                        default="gb",
                        help="The region that the caller id has originated from.  Only required when phone number" \
                             " is supplied without an international dialling code.  Must be in CCN format.  See" \
                             "CountryCodes.json",
                        required=False)

    parser.add_argument("--settings",
                        help="Path to Settings INI file",
                        dest="setting_path",
                        default="CallerLookup.ini",
                        required=False)

    parser.add_argument("--logdir",
                        help="Path to Log Directory",
                        dest="log_path",
                        default="logs",
                        required=False)

    parser.add_argument("--debug",
                        help="Debug mode",
                        action="store_true",
                        dest="is_debug")

    args = vars(parser.parse_args())
    lookup = ReverseLookup(args["setting_path"], args["log_path"], args["is_debug"])
    result = lookup.search(args["phone_number"], args["default_region"])

    print(json.dumps(result, indent=2))
