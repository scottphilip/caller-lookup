# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

import requests
import requests.adapters
import requests.packages.urllib3
from CallerLookup.Strings import CallerLookupKeys
from CallerLookup.Utils.Logs import *


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
        if self.config.is_debug():
            log_debug(self.config,
                      {
                          "REQUEST": {"URL": url,
                                      "HEADERS": str(headers).encode(encoding="UTF-8", errors="IGNORE")},
                          "RESPONSE": {"STATUS_CODE": response.status_code,
                                       "HEADERS": str(response.headers).encode(encoding="UTF-8", errors="IGNORE"),
                                       "DATA": response.text.encode(encoding="UTF-8", errors="IGNORE")}
                      })
        return response.status_code, response.headers, response.text

    def post(self, url, headers, data):
        try:
            encoded_data = bytes(data)
        except:
            encoded_data = bytes(data, encoding=CallerLookupKeys.UTF8)
        headers.update({CallerLookupKeys.HTTP_HEADER_CONTENT_LENGTH: str(len(encoded_data))})
        response = self.session.post(url, headers=headers, data=encoded_data)
        if self.config.is_debug():
            log_debug(self.config,
                      {
                          "REQUEST": {"URL": url,
                                      "HEADERS": str(headers).encode(encoding="UTF-8", errors="IGNORE"),
                                      "DATA": str(encoded_data).encode(encoding="UTF-8", errors="IGNORE")},
                          "RESPONSE": {"STATUS_CODE": response.status_code,
                                       "HEADERS": str(response.headers).encode(encoding="UTF-8", errors="IGNORE"),
                                       "DATA": response.text.encode(encoding="UTF-8", errors="IGNORE")}
                      })
        return response.status_code, response.headers, response.text
