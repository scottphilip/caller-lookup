# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (13 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from datetime import datetime, timedelta
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
                 cookies_storage_path=None,
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
        :param cookies_storage_path:
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
                                      cookie_storage_path=cookies_storage_path,
                                      cache_path=cache_path,
                                      is_debug=is_debug,
                                      image_path=image_path,
                                      phantomjs_log_path=phantomjs_log_path,
                                      logger=logger)

    def search(self, number, region=None, int_dial_code=None):
        """
        :param number:
        :param region:
        :param int_dial_code:
        :return:
        """

        log_debug(self.config, "Search", {"number": number, "region": region, "int_dial_code": int_dial_code})
        start_time = datetime.utcnow()

        try:

            cached = get_cached_response(self.config, phone_number=number)
            if cached is not None:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                if self.config.is_debug:
                    cached[CallerLookupLabel.TIME_TAKEN] = elapsed
                CallerLookupReport.record(number, region, int_dial_code, cached, elapsed)
                return cached

            number_data = format_number(number,
                                        trunk_int_dial_code=int_dial_code,
                                        trunk_country_code=region)

            if not number_data[CallerLookupLabel.IS_VALID]:
                return get_response_invalid(number, region)

            data = get_search_response_data(self.config, number_data)

            result = get_response_success(number_data, data)

            set_cached_response(self.config, number, result)

            elapsed = datetime.utcnow() - start_time
            if self.config.is_debug:
                result[CallerLookupLabel.TIME_TAKEN] = elapsed.total_seconds()
            CallerLookupReport.record(number, region, int_dial_code, result, elapsed)
            return result

        except Exception as e:

            import traceback
            log_error(self.config, "SEARCH_ERROR",
                      {"Exception": str(e),
                       "Stack": traceback.format_exc()})
            if self.config.is_debug:
                raise
            response = get_response_error(str(e))
            elapsed = datetime.utcnow() - start_time
            CallerLookupReport.record(number, region, int_dial_code, response, elapsed)
            pass



