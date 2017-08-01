# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup.Responses import *
from CallerLookup.Search import *
from CallerLookup.Utils.Report import record
from CallerLookup.Strings import CallerLookupLabel, CallerLookupConfigStrings
from CallerLookup.Configuration import CallerLookupConfiguration, extract_values
from CallerLookup.Utils.PhoneNumbers import format_number
from datetime import datetime
from sys import exc_info
import traceback


# noinspection PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,
# PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,
# PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,
# PyIncorrectDocstring
def lookup_number(**kwargs):
    """
    :param NUMBER               Phone number to lookup
    :param REGION               Region the trunk belongs to (eg; GB, DE, US)
    :param REGION_DIAL_CODE     Region Dial Code the trunk belongs to (eg; 44, 49, 1)
    :param PHANTOMJS_PATH       Path to PhantomJS binary
    :param IS_CACHE_ENABLED     Enabled result Cache
    :param IS_DEBUG             Debug Mode
    :param USERNAME             Google Account Username
    :param PASSWORD             Google Account Password
    :param SECRET               Google Account Secret (OTP secret where account has
                                two step authentication enabled
    :param IS_SAVE_CREDENTIALS  Save the credentials to the configuration
    :param REMOVE_ACCOUNT       Remove account details from configuration
    :param SET_DEFAULT          Set the default account to use
    :param CONFIG_DIR           Configuration Directory Path
    :param DATA_DIR             Data Directory Path
    :param LOG_DIR              Log Directory Path
    :return:                    Dictionary
    """
    search_args = extract_values([CallerLookupConfigStrings.NUMBER,
                                  CallerLookupConfigStrings.REGION,
                                  CallerLookupConfigStrings.REGION_DIAL_CODE], **kwargs)

    with CallerLookup(**kwargs) as lookup:
        log_debug(lookup.config, "ARGS", str(kwargs))
        if not search_args[CallerLookupConfigStrings.NUMBER]:
            return
        return lookup.search(number=search_args[CallerLookupConfigStrings.NUMBER],
                             region=search_args[CallerLookupConfigStrings.REGION],
                             region_dial_code=search_args[CallerLookupConfigStrings.REGION_DIAL_CODE])


class CallerLookup(object):
    """
    Caller Lookup - Reverse Caller Id
    """
    config = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if key.upper() == CallerLookupConfigStrings.CONFIG:
                self.config = kwargs.pop(key)
                break
        if self.config is None:
            self.config = CallerLookupConfiguration(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.config.save()

    def search(self, number, region=None, region_dial_code=None):
        start_time = datetime.utcnow()
        response = self._do_search(number, region, region_dial_code)
        elapsed_seconds = (datetime.utcnow() - start_time).total_seconds()
        if self.config.is_debug():
            response[CallerLookupLabel.TIME_TAKEN] = elapsed_seconds
        record(self.config, number, region, region_dial_code, response, elapsed_seconds)
        return response

    def _do_search(self, number, region=None, region_dial_code=None):
        log_debug(self.config, "SEARCH", number, region, region_dial_code)
        try:
            cached = get_cached_response(self.config, phone_number=number)
            if cached is not None:
                return cached
            number_data = format_number(self.config,
                                        number,
                                        trunk_int_dial_code=region_dial_code,
                                        trunk_country_code=region)
            if not number_data[CallerLookupLabel.IS_VALID]:
                return get_response_invalid(number, region)
            data = run_search(self.config, number_data)
            result = get_response_success(number_data, data)
            set_cached_response(self.config, number, result)
            return result
        except Exception as ex:
            stack = traceback.format_exc()
            log_error(self.config, "SEARCH_ERROR",
                      {"MESSAGE": format_exception(ex),
                       "STACK": stack})
            return get_response_error(ex)
