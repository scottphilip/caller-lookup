# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup.Strings import CallerLookupLabel, CallerLookupKeys
from CallerLookup.Utils.Logs import format_exception


def get_response_invalid(number, region):
    return {CallerLookupLabel.RESULT: CallerLookupLabel.INVALID_NUMBER,
            CallerLookupLabel.NUMBER: number,
            CallerLookupLabel.REGION: region}


def get_response_error(ex):
    result = {CallerLookupLabel.RESULT: CallerLookupLabel.ERROR,
              CallerLookupLabel.MESSAGE: format_exception(ex)}
    return result


def get_response_success(number_data, data):
    result = {CallerLookupLabel.RESULT: CallerLookupLabel.UNKNOWN,
              CallerLookupLabel.SCORE: 100}
    result.update(number_data)

    if data is None or CallerLookupKeys.KEY_DATA not in data:
        return result
    data = data[CallerLookupKeys.KEY_DATA]

    if len(data) == 0:
        return result
    data = data[0]

    if CallerLookupKeys.KEY_SCORE in data:
        result[CallerLookupLabel.SCORE] = round(data[CallerLookupKeys.KEY_SCORE] * 100)

    if CallerLookupKeys.KEY_ADDRESSES in data:
        addresses = data[CallerLookupKeys.KEY_ADDRESSES]
        if len(addresses) > 0:
            if CallerLookupKeys.KEY_COUNTRY_CODE in addresses[0]:
                result[CallerLookupLabel.REGION] = \
                    addresses[0][CallerLookupKeys.KEY_COUNTRY_CODE].upper()
            if CallerLookupKeys.KEY_ADDRESS in addresses[0]:
                result[CallerLookupLabel.ADDRESS] = \
                    addresses[0][CallerLookupKeys.KEY_ADDRESS]

    if CallerLookupKeys.KEY_NAME in data:
        result[CallerLookupLabel.NAME] = data[CallerLookupKeys.KEY_NAME]
        result[CallerLookupLabel.RESULT] = CallerLookupLabel.SUCCESS

    return result
