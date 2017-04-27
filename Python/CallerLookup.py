#!/usr/bin/python
import argparse
import configparser
import datetime
import gzip
import http.cookiejar
import json
import logging
import os
import time
import urllib
import urllib.parse
import urllib.request

import phonenumbers
import requests.cookies
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class CallerLookup(object):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36"
    default_headers = {"Accept": "application/json, text/plain, */*",
                       "Accept-Language": "en-US",
                       "Accept-Encoding": "gzip, deflate",
                       "Connection": "Keep-Alive",
                       "User-Agent": user_agent}
    url_search = 'https://www.truecaller.com/api/search?{}'
    url_token = "https://www.truecaller.com/api/auth/google?clientId=4"
    url_token_callback = "https://www.truecaller.com/auth/google/callback"

    def __init__(self, settings):
        global log_helper
        if log_helper is None:
            log_helper = self.LogHelper(settings)

        log_helper.debug("#############################################################################")
        log_helper.debug("{:20} {}".format("ARGS", str(settings)))

        self._generator = CallerLookup.TokenGenerator(settings)
        self.settings = settings

    def search(self, phone_number, default_region):
        start = time.time()
        result = self._search(phone_number, default_region)
        elapsed = time.time() - start
        if self.settings["is_debug"]:
            result["time_taken"] = str(elapsed)
        return result

    def _search(self, phone_number, default_region):

        def format_phone_number(format_number, format_region):
            format_valid = False
            try:
                phone_number = phonenumbers.parse(format_number, format_region.upper())
                format_region = get_phone_number_region(str(phone_number.country_code), format_region).upper()
                format_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
                format_valid = phonenumbers.is_valid_number(phone_number)
            except:
                ignore = True
            return format_valid, format_number, format_region

        def get_phone_number_region(country_dial_code, provided_region):
            try:
                country_data = json.loads(open(self.settings["country_data_path"]).read())
                for country in country_data:
                    if country["CC"] == country_dial_code:
                        return country["CCN"]
            except Exception as e:
                log_helper.error("{:20} Error Loading Country Code Data: {}".format("COUNTRY DATA", str(e)))
            return provided_region

        def get_response_invalid(number, region):
            return {"result": "invalid_number",
                    "number": number,
                    "region": region}

        def get_response_error(message):
            return {"result": "error",
                    "message": message}

        def get_response_success(number, region, name, score):
            return {"result": "success",
                    "number": number,
                    "region": region,
                    "name": name,
                    "score": score}

        (is_valid_number, phone_number, default_region) = format_phone_number(phone_number,
                                                                              default_region)
        if not is_valid_number:
            log_helper.info("{:20s} {:30s} {} ({})".format("SEARCH",
                                                           "Invalid Number",
                                                           phone_number,
                                                           default_region))
            return get_response_invalid(phone_number, default_region)

        log_helper.info("{:20s} {:30s} {} ({})".format("SEARCH",
                                                       "PARAMETERS",
                                                       phone_number,
                                                       default_region))
        try:
            fail_count = 0
            query = self.url_search.format(urllib.parse.urlencode({"type": 4,
                                                                   "countryCode": default_region,
                                                                   "q": phone_number}))
            with CallerLookup.HttpHandler(self.settings["cookies_path"], CallerLookup.user_agent) as handler:
                while fail_count <= 1:
                    ignore_cache = fail_count > 0
                    token = self._generator.token(handler, ignore_cache)
                    if token is None:
                        fail_count += 1
                        continue
                    (token_res_code, token_res_data, token_res_header) = handler.http_get(query, [
                        ("Authorization", "Bearer {}".format(token)),
                        ("Host", "www.truecaller.com"),
                        ("Referer", "https://www.truecaller.com/")])
                    if token_res_code == 200:
                        return self._format_data(token_res_data, phone_number, default_region)
                    elif token_res_code == 401:
                        log_helper.info("Token {} has expired.".format(token))
                    else:
                        log_helper.info(
                            "Token {} resulted in status code: {} ".format(token, token_res_code, token_res_data))
                    fail_count += 1

            raise Exception("Failed {} times attempting query {}".format(fail_count, query))

        except Exception as e:
            log_helper.error(str(e))
            raise

    def _format_data(self, result_data, phone_number, default_region):
        result = {"result": "unknown",
                  "number": phone_number,
                  "region": default_region}
        data = json.loads(result_data)
        if "data" in data:
            data = data["data"]
        if len(data) > 0:
            data = data[0]
        if "score" in data:
            result["score"] = data["score"]
        if "addresses" in data:
            addresses = data["addresses"]
            if len(addresses) > 0:
                if "countryCode" in addresses[0]:
                    result["region"] = addresses[0]["countryCode"].upper()
        if "name" in data:
            result["name"] = data["name"]
            result["result"] = "success"
            log_helper.info("{:20s} {:30s} {}".format("SEARCH",
                                                      "RESULT",
                                                      str(result)))
            return result
        return result

    def _get_search_result(self, url, token):
        is_success = False
        data = {}
        return (is_success, data)

    class OAuthRequest(object):
        protocol = "https"
        domain = "accounts.google.com"
        path = "/o/oauth2/v2/auth"
        data = {"response_type": "token",
                "client_id": "1051333251514-p0jdvav4228ebsu820jd3l3cqc7off2g.apps.googleusercontent.com",
                "redirect_uri": "https://www.truecaller.com/auth/google/callback",
                "scope": "https://www.googleapis.com/auth/userinfo.email "
                         "https://www.googleapis.com/auth/userinfo.profile "
                         "https://www.google.com/m8/feeds/"}

        @staticmethod
        def get_url():
            return "{}://{}{}?{}" \
                .format(CallerLookup.OAuthRequest.protocol,
                        CallerLookup.OAuthRequest.domain,
                        CallerLookup.OAuthRequest.path,
                        urllib.parse.urlencode(CallerLookup.OAuthRequest.data))

    class TokenGenerator(object):

        url_accounts = "https://accounts.google.com"
        url_myaccount = "https://myaccount.google.com"
        url_accounts_servicelogin = "{}/ServiceLogin".format(url_accounts)
        url_accounts_noform = "{}/x".format(url_accounts)

        def __init__(self, settings):

            self.setting_path = settings["setting_path"]
            self.cookies_path = settings["cookies_path"]

            if "username" in settings and not settings["username"] is None:
                self.username = settings["username"]
                if not "password" in settings:
                    raise Exception("Password must be supplied with username")
                self.password = settings["password"]
                if "otpsecret" in settings:
                    self.otpsecret = settings["otpsecret"]
                else:
                    self.otpsecret = None

            else:

                self.username = CallerLookup.SettingHelper \
                    .get_setting(self.setting_path, "Credentials", "username")
                if self.username is None:
                    raise Exception("Configuration Error.  Username is not set {}".format(self.setting_path))

                self.password = CallerLookup.SettingHelper \
                    .get_setting(self.setting_path, "Credentials", "password")
                if self.password is None:
                    raise Exception("Configuration Error.  Password is not set {}".format(self.setting_path))

                self.otpsecret = CallerLookup.SettingHelper \
                    .get_setting(self.setting_path, "Credentials", "otpsecret")

        def token(self, handler, ignore_cache=False):
            if not ignore_cache:
                cache_date = CallerLookup.SettingHelper.get_setting(self.setting_path, "Cache", "TokenExpiry")
                if cache_date is not None and datetime.datetime.strptime(cache_date, "%Y-%m-%d %H:%M:%S") \
                        > datetime.datetime.now():
                    token = CallerLookup.SettingHelper.get_setting(self.setting_path, "Cache", "Token")
                    log_helper.debug("Cached Token: " + token)
                    return token
            return self._get_new_token(handler)

        def _get_new_token(self, handler):

            def _get_refreshed_token():
                url = CallerLookup.OAuthRequest.get_url()
                if not handler.is_cookie_available(url):
                    return None
                (oauth_res_code, oauth_res_data, oauth_res_header) = handler.http_get(url)
                if oauth_res_code != 302 or not "location" in oauth_res_header:
                    return None
                redirect_location = oauth_res_header["location"]
                log_helper.debug("{:20} {:30} {}".format("REFRESH TOKEN", "Redirect Url", redirect_location))
                if redirect_location.count(self.url_accounts) > 0:
                    return None
                if redirect_location.count("#") == 0:
                    return None
                query_string_data = redirect_location.split("#")[1]
                log_helper.debug("{:20} {:30} {}".format("REFRESH TOKEN", "Querystring Data", query_string_data))
                oauth_data = urllib.parse.parse_qs(query_string_data)
                oauth_token = oauth_data["access_token"][0]
                log_helper.debug("{:20} {:30} {}".format("REFRESH TOKEN", "Oauth Token", oauth_token))
                request_data = '{"accessToken":"'+oauth_token+'"}'
                handler.http_get(redirect_location, None)
                (token_res_code, token_res_data, token_res_header) = handler \
                    .http_post(CallerLookup.url_token, request_data, {#"content-length":len(str(request_data)),
                    "content-type": "application/json",
                                                                       "referer": "https://www.truecaller.com/auth/google/callback",
                                                                       "origin": "https://www.truecaller.com"})
                if token_res_code != 200:
                    return None
                refreshed_token = json.loads(token_res_data)
                if not "accessToken" in refreshed_token:
                    return None
                refreshed_access_token = refreshed_token["accessToken"]
                log_helper.debug("{:20} {:30} {}".format("REFRESH TOKEN", "Success", refreshed_access_token))
                return refreshed_access_token

            def _get_restart_token():
                def wait_for(condition_function, timeout):
                    start_time = time.time()
                    while time.time() < start_time + timeout:
                        if condition_function():
                            return True
                        else:
                            time.sleep(0.1)
                    return False

                def get_otp():
                    if self.otpsecret is None:
                        save_screenshot("TwoFactorAuth")
                        raise Exception("Sign in requires Two Step authentication but otpsecret has not been set.")
                    import pyotp
                    return pyotp.TOTP(self.otpsecret)

                def is_token_created():
                    return driver.execute_script("return localStorage.getItem('tcToken') != null")

                def restore_cookies():
                    log_helper.debug("Restoring Cookies...")
                    cookies = handler.get_cookies(CallerLookup.TokenGenerator.url_accounts_noform)
                    if cookies is None or len(cookies) == 0:
                        return
                    driver.get(CallerLookup.TokenGenerator.url_accounts_noform)
                    for cookie in cookies:
                        try:
                            driver.add_cookie(cookie)
                        except:
                            ignore = True

                def save_cookies():
                    if driver.current_url.count(CallerLookup.TokenGenerator.url_accounts) == 0:
                        driver.get(CallerLookup.TokenGenerator.url_accounts_noform)
                    handler.set_cookies(driver.get_cookies())

                def save_screenshot(name):
                    save_path = os.path.join(log_helper.path, "ScreenShots")
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                    save_path = os.path.join(save_path, "{}-{}.png".format(
                        str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")), name))
                    log_helper.debug("Screenshot URL={} Image=>{}"
                                     .format(driver.current_url, save_path))
                    driver.save_screenshot(save_path)

                log_helper.debug("===================")
                log_helper.debug("    WEBDRIVER")
                log_helper.debug("===================")

                driver = webdriver.PhantomJS(
                    service_log_path=os.path.join(log_helper.path, "CountryCodes.WebDriver.log"))
                try:
                    delay = 3
                    driver.set_window_size(600, 800)
                    restore_cookies()
                    url_login = CallerLookup.OAuthRequest.get_url()
                    log_helper.debug("GoTo URL={}".format(url_login))
                    driver.get(url_login)
                    if driver.current_url.startswith(self.url_accounts):
                        log_helper.debug("Completing Logon Form (current_url={})".format(driver.current_url))
                        email_element = driver.find_element_by_id('Email')
                        if email_element is not None:
                            log_helper.debug("Completing Username (current_url={})".format(driver.current_url))
                            email_element.send_keys(self.username)
                            driver.find_element_by_id("next").click()
                        WebDriverWait(driver, delay).until(ec.element_to_be_clickable((By.ID, "Passwd")))
                        driver.find_element_by_id('Passwd').send_keys(self.password)
                        driver.find_element_by_id("signIn").click()
                        if driver.current_url.count("challenge/totp") > 0:
                            WebDriverWait(driver, delay).until(ec.element_to_be_clickable((By.ID, "totpPin")))
                            driver.find_element_by_id('totpPin').send_keys(get_otp())
                            driver.find_element_by_id("submit").click()
                        if driver.current_url.count("challenge/az") > 0: #Phone Challenge
                            if not wait_for(is_token_created, 300):
                                raise Exception("Time out waiting for phone to accept login.")
                        save_cookies()
                    driver.get(url_login)
                    if wait_for(is_token_created, delay):
                        return driver.execute_script("return localStorage.getItem('tcToken')")
                    save_screenshot("TimedOut")
                    return None
                except:
                    save_screenshot("ErrorScreenshot")
                    raise

            token = _get_refreshed_token()
            if token is None:
                token = _get_restart_token()
            if token is None:
                raise Exception("Failed to create new token")

            if token.startswith('"') and token.endswith('"'):
                token = token[1:-1]
            log_helper.debug("Saving Token to Cache")
            expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
            CallerLookup.SettingHelper.set_setting(self.setting_path, "Cache", "TokenExpiry",
                                                    expiry.strftime("%Y-%m-%d %H:%M:%S"))
            CallerLookup.SettingHelper.set_setting(self.setting_path, "Cache", "Token", token)
            return token

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
            self.path = os.path.dirname(settings["log_path"])
            self.log_path = settings["log_path"]
            self.is_debug = settings["is_debug"]

            if len(self.path) > 0:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)

            logging.getLogger().setLevel(logging.INFO)
            self._log = logging.getLogger("CallerLookup")
            handler = logging.FileHandler(self.log_path)
            formatter = logging.Formatter('%(asctime)s   >>   %(levelname)8s   >>   %(message)s')
            handler.setFormatter(formatter)
            self._log.addHandler(handler)
            self._log.setLevel(logging.INFO)

            if self.is_debug:
                logging.getLogger().setLevel(logging.DEBUG)
                self._log.setLevel(logging.DEBUG)
                req_log = logging.getLogger("requests.packages.urllib3")
                req_log.setLevel(logging.DEBUG)
                req_log.propagate = True
                req_handler = logging.FileHandler(os.path.join(self.path, "CallerLookup.HttpHandler.log"))
                req_handler.setFormatter(formatter)
                req_log.addHandler(req_handler)

        def debug(self, message):
            """Log Debug Message"""
            self._log.debug(message.encode(sys.stdout.encoding, errors='replace'))

        def info(self, message):
            """Log Info Message"""
            self._log.info(message.encode(sys.stdout.encoding, errors='replace'))

        def warning(self, message):
            """Log Warning Message"""
            self._log.warning(message.encode(sys.stdout.encoding, errors='replace'))

        def error(self, message):
            """Log Error Message"""
            self._log.error(message.encode(sys.stdout.encoding, errors='replace'))

    class HttpHandler(object):

        class NoRedirect(urllib.request.HTTPErrorProcessor):
            def http_response(self, request, response):
                return response

            https_response = http_response

        def __init__(self, storage_path, user_agent):
            self.user_agent = user_agent
            self.storage_path = storage_path

        def __enter__(self):
            self._cookiejar = http.cookiejar.MozillaCookieJar()
            if os.path.isfile(self.storage_path):
                self._cookiejar.load(self.storage_path, ignore_discard=True)
            self._opener = urllib.request.build_opener(CallerLookup.HttpHandler.NoRedirect,
                                                 urllib.request.HTTPCookieProcessor(self._cookiejar))
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.save_cookies()

        @staticmethod
        def get_headers(append_headers=None, include_default=True):
            result = {}
            if append_headers is not None:
                result.update(append_headers)  # result.update(append_headers)
            if include_default:
                result.update(CallerLookup.default_headers)
            return result

        def http_get(self, url, headers=None, include_default_headers=True):
            return self._http_request("GET", url, None, headers, include_default_headers)

        def http_post(self, url, data, headers=None, include_default_headers=True):
            return self._http_request("POST", url, data, headers, include_default_headers)

        def _http_request(self, method, url, data=None, headers=None, include_default_headers=True):


            log_helper.debug("===================")
            log_helper.debug("    {} REQUEST".format(method))
            log_helper.debug("===================")
            log_helper.debug("{:20s} {}".format("URL", url))

            add_headers = self.get_headers(headers, include_default_headers)
            encoded_data = None
            if not data is None:
                encoded_data = bytes(data, "utf-8")
                #encoded_data = gzip.compress(data)
                #encoded_data = str(data).encode('utf-8')
                add_headers.update({"content-length": len(encoded_data)})

            request = urllib.request.Request(url, data=encoded_data, headers=add_headers, method=method)

            if not data is None:
                log_helper.debug("{:20s} \n{}".format("DATA", data))
                log_helper.debug("{:20s} \n{}".format("DATA (Encoded)", encoded_data))

            try:
                response = self._opener.open(request)
            finally:
                log_helper.debug("{:20s} \n{}".format("HEADERS", json.dumps(request.header_items())))

            log_helper.debug("===================")
            log_helper.debug("    {} RESPONSE".format(method))
            log_helper.debug("===================")
            response_code = response.getcode()
            log_helper.debug("{:20s} {}".format("STATUS CODE", response_code))
            response_headers = response.info()
            import collections
            result_dict = collections.defaultdict(list)
            for key, value in response_headers.items():
                result_dict[key].append(value)
            log_helper.debug("{:20s} \n{}".format("HEADERS", json.dumps(result_dict)))
            if response_headers.get('Content-Encoding') == 'gzip':
                response_data = gzip.GzipFile(fileobj=response).read().decode("utf-8")
            else:
                response_data = response.read()
            log_helper.debug("{:20s} {}".format("DATA", response_data))

            return response_code, response_data, response_headers



        def get_cookies(self, full_url):
            url = urllib.parse.urlparse(full_url)
            domain = url.netloc
            request_jar = requests.cookies.RequestsCookieJar()
            request_jar.update(self._cookiejar)
            return request_jar.get_dict(domain)

        def is_cookie_available(self, full_url):
            return len(self.get_cookies(full_url)) > 0

        def set_cookies(self, cookies):
            for c in cookies:
                self._cookiejar.set_cookie(self._get_cookie(c))

        def save_cookies(self):
            self._cookiejar.save(self.storage_path, ignore_discard=True, )

        @staticmethod
        def _get_cookie(item):
            if item is None:
                return None
            return http.cookiejar.Cookie(item["version"] if "version" in item else None,
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
                                         None)

log_helper = None

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Reverse Caller Id',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="Example: {0} --number +12024561111\n" 
                                            "         {0} --number 02079309000 --region gb"
                                     .format(os.path.basename(__file__)))

    default_directory = os.path.join(os.path.expanduser("~"), ".CallerLookup")

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
                        default=os.path.join(default_directory, "CallerLookup.ini"),
                        required=False)

    parser.add_argument("--cookies",
                        help="Path to Cookie store file",
                        dest="cookies_path",
                        default=os.path.join(default_directory, "CallerLookup.cookies"),
                        required=False)

    parser.add_argument("--countrycodes",
                        help="Path to Country Codes data file",
                        dest="country_data_path",
                        default=os.path.join(default_directory, "CountryCodes.json"),
                        required=False)

    parser.add_argument("--username",
                        help="Google Account Username",
                        dest="username",
                        required=False)

    parser.add_argument("--password",
                        help="Google Account Password",
                        dest="password",
                        required=False)

    parser.add_argument("--otpsecret",
                        help="Google Account Two-Factor Auth Secret",
                        dest="otpsecret",
                        required=False)

    parser.add_argument("--logpath",
                        help="Path to Log Directory",
                        dest="log_path",
                        default=os.path.join(default_directory, "CallerLookup.log"),
                        required=False)

    parser.add_argument("--debug",
                        help="Debug mode",
                        action="store_true",
                        dest="is_debug")

    args = vars(parser.parse_args())

    try:
        lookup = CallerLookup(args)
        result = lookup.search(args["phone_number"], args["default_region"])

        print(str(result))
        exit(0)

    except Exception as e:

        print(str({"Result": "Error", "Error": str(e)}))
        raise
