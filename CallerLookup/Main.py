from time import time
from CallerLookup.Configuration import CallerLookupConfiguration
from CallerLookup.Responses import *
from CallerLookup.Search import *
from CallerLookup.Strings import CallerLookupLabel


class CallerLookup(object):
    """

    """

    def __init__(self,
                 google_account_username,
                 google_account_password=None,
                 google_account_otp_secret=None,
                 phantomjs_path=None,
                 cookies_path=None,
                 cache_path=None,
                 is_debug=False,
                 image_path=None,
                 phantomjs_log_path=None,
                 config=None):
        """
        :param google_account_username:
        :param google_account_password:
        :param google_account_otp_secret:
        :param phantomjs_path:
        :param cookies_path:
        :param cache_path:
        :param is_debug:
        :param image_path:
        :param phantomjs_log_path:
        :param config:
        """

        self.config = config if config is not None else \
            CallerLookupConfiguration(google_account_username=google_account_username,
                                      google_account_password=google_account_password,
                                      google_account_otp_secret=google_account_otp_secret,
                                      phantomjs_path=phantomjs_path,
                                      cookies_path=cookies_path,
                                      cache_path=cache_path,
                                      is_debug=is_debug,
                                      image_path=image_path,
                                      phantomjs_log_path=phantomjs_log_path)

    def search(self, number, region=None, int_dial_code=None):
        """
        :param number:
        :param region:
        :param int_dial_code:
        :return:
        """
        start_time = time() if self.config.is_debug else None
        number_data = format_number(number,
                               trunk_int_dial_code=int_dial_code,
                               country_code=region)
        if not number[CallerLookupLabel.IS_VALID]:
            return get_response_invalid(number, region)

        data = get_search_response_data(self.config, number_data)

        return get_response_success(data, start_time)





