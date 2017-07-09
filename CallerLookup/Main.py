# Author:       Scott Philip (sp@scottphilip.com)
# Version:      0.1 (10 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from time import time
from CallerLookup.Configuration import CallerLookupConfiguration
from CallerLookup.Responses import *
from CallerLookup.Search import *
from CallerLookup.Strings import CallerLookupLabel


class CallerLookup(object):
    """
    Caller Lookup - Reverse Caller Id
    """

    def __init__(self,
                 account_email=None,
                 account_password=None,
                 account_otp_secret=None,
                 phantomjs_path=None,
                 cookies_path=None,
                 cache_path=None,
                 is_debug=False,
                 image_path=None,
                 phantomjs_log_path=None,
                 logger=None,
                 config=None):
        """
        :param account_email:
        :param account_password:
        :param account_otp_secret:
        :param phantomjs_path:
        :param cookies_path:
        :param cache_path:
        :param is_debug:
        :param image_path:
        :param phantomjs_log_path:
        :param config:
        """

        self.config = config if config is not None else \
            CallerLookupConfiguration(account_email=account_email,
                                      account_password=account_password,
                                      account_otp_secret=account_otp_secret,
                                      phantomjs_path=phantomjs_path,
                                      cookies_path=cookies_path,
                                      cache_path=cache_path,
                                      is_debug=is_debug,
                                      image_path=image_path,
                                      phantomjs_log_path=phantomjs_log_path,
                                      logger=logger)
        self.http = CallerLookupHttp(self.config)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.http.save_cookies()

    def search(self, number, region=None, int_dial_code=None):
        """
        :param number:
        :param region:
        :param int_dial_code:
        :return:
        """

        log_debug(self.config, "Search", {"number": number, "region": region, "int_dial_code": int_dial_code})

        try:

            start_time = time() if self.config.is_debug else None

            number_data = format_number(number,
                                        trunk_int_dial_code=int_dial_code,
                                        country_code=region)

            if not number_data[CallerLookupLabel.IS_VALID]:
                return get_response_invalid(number, region)

            data = get_search_response_data(self.config, self.http, number_data)

            return get_response_success(number_data, data, start_time)

        except Exception as e:


            log_error(self.config, "SEARCH_ERROR", Exception=e)
            if self.config.is_debug:
                raise
            return get_response_error(str(e))
            pass



