# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (20 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup.Responses import *
from CallerLookup.Search import *
from CallerLookup.Strings import CallerLookupLabel, CallerLookupConfigStrings
from CallerLookup.Configuration import CallerLookupConfiguration, extract_values
from CallerLookup.Utils.PhoneNumbers import format_number
from datetime import datetime


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
        log_debug(lookup.config, {"DATA_DIR": lookup.config.data_dir,
                                  "LOG_DIR": lookup.config.log_dir,
                                  "CONFIG_DIR": lookup.config.config_dir,
                                  "SETTINGS": str(lookup.config.settings),
                                  "RUNTIME": str(lookup.config.runtime)})
        if not search_args[CallerLookupConfigStrings.NUMBER]:
            return
        return lookup.search(number=search_args[CallerLookupConfigStrings.NUMBER],
                             region=search_args[CallerLookupConfigStrings.REGION],
                             region_dial_code=search_args[CallerLookupConfigStrings.REGION_DIAL_CODE])


class CallerLookup(object):
    """
    Caller Lookup - Reverse Caller Id
    """

    def __init__(self, **kwargs):
        self.config = CallerLookupConfiguration(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.config.save()

    def search(self, number, region=None, region_dial_code=None):
        """
        :param number:
        :param region:
        :param region_dial_code:
        :return:
        """

        log_debug(self.config, "Search", {"number": number, "region": region, "int_dial_code": region_dial_code})
        start_time = datetime.utcnow()

        try:

            cached = get_cached_response(self.config, phone_number=number)
            if cached is not None:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                if self.config.is_debug():
                    cached[CallerLookupLabel.TIME_TAKEN] = elapsed
                return cached

            number_data = format_number(number,
                                        trunk_int_dial_code=region_dial_code,
                                        trunk_country_code=region)

            if not number_data[CallerLookupLabel.IS_VALID]:
                return get_response_invalid(number, region)

            data = run_search(self.config, number_data)
            result = get_response_success(number_data, data)
            set_cached_response(self.config, number, result)

            if self.config.is_debug():
                elapsed = datetime.utcnow() - start_time
                result[CallerLookupLabel.TIME_TAKEN] = elapsed.total_seconds()
            return result

        except Exception as e:

            import traceback
            stack = traceback.format_exc()
            log_error(self.config, "SEARCH_ERROR",
                      {"Exception": str(e),
                       "Stack": stack})
            response = get_response_error(str(e), stack if self.config.is_debug() else None)
            return response
