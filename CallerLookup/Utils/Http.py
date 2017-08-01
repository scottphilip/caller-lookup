# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

import requests
import requests.adapters
import requests.packages.urllib3
import json
from CallerLookup.Strings import CallerLookupKeys
from CallerLookup.Utils.Logs import *


class HttpException(Exception):
    status_code = 0
    message = ""

    def __init__(self, status_code, message):
        super(HttpException, self).__init__(message, status_code)
        self.status_code = status_code
        self.message = message


class CallerLookupHttp(object):
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            self.session.close()

    def get(self, url, headers):
        response = self.session.get(url, headers=headers)
        self.log_http_response(request_url=url, request_headers=headers,
                               response=response)
        return response.status_code, response.headers, response.text

    def post(self, url, headers, data):
        try:
            encoded_data = bytes(data)
        except:
            encoded_data = bytes(data, encoding=CallerLookupKeys.UTF8)
        headers.update({CallerLookupKeys.HTTP_HEADER_CONTENT_LENGTH: str(len(encoded_data))})
        response = self.session.post(url, headers=headers, data=encoded_data)
        self.log_http_response(request_url=url, request_headers=headers,
                               request_data=str(encoded_data), response=response)
        return response.status_code, response.headers, response.text

    def log_http_response(self, request_url, request_headers, response, request_data=None):
        store = {
            "REQUEST": {"URL": request_url,
                        "HEADERS": str(request_headers).encode(encoding="UTF-8", errors="IGNORE")},
            "RESPONSE": {"STATUS_CODE": response.status_code,
                         "HEADERS": str(response.headers).encode(encoding="UTF-8", errors="IGNORE"),
                         "DATA": response.text.encode(encoding="UTF-8", errors="IGNORE")}
        }
        if request_data is not None:
            store["REQUEST"]["DATA"] = str(request_data).encode(encoding="UTF-8", errors="IGNORE")
        if response.status_code >= 400:
            message = "HTTP ERROR CODE " + str(response.status_code)
            try:
                data = json.loads(store["RESPONSE"]["DATA"])
                for key in data:
                    if key.upper() == "MESSAGE":
                        message = data[key]
                        break
            except:
                ignore=True
            log_error(self.config, "HTTP_INVALID_STATUS", message, store)
            raise HttpException(message=message, status_code=response.status_code)
        else:
            log_debug(self.config, store)
