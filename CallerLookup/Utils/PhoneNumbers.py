# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup.Strings import CallerLookupLabel
from phonenumbers import parse, is_valid_number, format_number as fmt_number, PhoneNumberFormat, \
    region_code_for_number, UNKNOWN_REGION
from CallerLookup.CountryCodes import CallerLookupCountryCodes
from CallerLookup.Utils.Logs import *


def format_number(config, phone_number, trunk_int_dial_code=None, trunk_country_code=None):
    o = None
    result = {CallerLookupLabel.IS_VALID: False}
    region = trunk_country_code.upper() if trunk_country_code else None
    int_dial_code = trunk_int_dial_code
    try:
        if region:
            o = parse(phone_number, region)
        else:
            if int_dial_code is not None:
                country_data = CallerLookupCountryCodes.get_country_data(country_int_dial_code=int_dial_code)
                for country in country_data:
                    region = country[CallerLookupLabel.COUNTRY_CODE].upper()
                    o = parse(phone_number, region)
        if o is None:
            o = parse(phone_number, UNKNOWN_REGION) if o is None else o
        result[CallerLookupLabel.IS_VALID] = is_valid_number(o)
        if result[CallerLookupLabel.IS_VALID]:
            result[CallerLookupLabel.NUMBER_E164] = fmt_number(o, PhoneNumberFormat.E164)
            result[CallerLookupLabel.NUMBER_NATIONAL] = fmt_number(o, PhoneNumberFormat.NATIONAL)
            result[CallerLookupLabel.REGION] = region_code_for_number(o)
            result[CallerLookupLabel.REGION_DIAL_CODE] = o.country_code
    except Exception as ex:
        log_debug(config, ["FORMAT_NUMBER_ERROR", str(ex)])

    return result

