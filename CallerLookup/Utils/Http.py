# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (20 July 2017)
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

    def get(self, url, headers):
        response = self.session.get(url, headers=headers)
        if self.config.is_debug():
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
        if self.config.is_debug():
            log_debug(self.config,
                      {
                          "REQUEST": {"URL": url, "HEADERS": str(headers), "DATA": encoded_data},
                          "RESPONSE": {"STATUS_CODE": response.status_code,
                                       "HEADERS": str(response.headers), "DATA": response.text}
                      })
        return response.status_code, response.headers, response.text
