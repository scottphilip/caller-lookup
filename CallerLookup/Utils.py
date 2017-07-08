from CallerLookup.CountryCodes import CallerLookupCountryCodes
from CallerLookup.Strings import CallerLookupLabel, CallerLookupErrors


def format_number(phone_number, trunk_int_dial_code=None, country_code=None):
    from phonenumbers import parse, is_valid_number, format_number, PhoneNumberFormat
    result = {CallerLookupLabel.IS_VALID: False}
    country_data = CallerLookupCountryCodes.get_country_data(country_int_dial_code=trunk_int_dial_code,
                                                             country_code=country_code)
    if country_data is None:
        raise Exception(CallerLookupErrors.COUNTRY_NOT_FOUND)
    if CallerLookupLabel.COUNTRY_CODE not in country_data:
        raise Exception(CallerLookupErrors.INVALID_COUNTRY_DATA)
    trunk_region = country_data[CallerLookupLabel.COUNTRY_CODE]
    o = parse(phone_number, trunk_region)
    result[CallerLookupLabel.IS_VALID] = is_valid_number(o)
    if result[CallerLookupLabel.IS_VALID]:
        result[CallerLookupLabel.NUMBER_E164] = format_number(o, PhoneNumberFormat.E164)
        result[CallerLookupLabel.NUMBER_NATIONAL] = format_number(o, PhoneNumberFormat.NATIONAL)
        result[CallerLookupLabel.REGION] = trunk_region
        result[CallerLookupLabel.REGION_DIAL_CODE] = country_data[CallerLookupLabel.REGION_DIAL_CODE]
    return result


def log_debug(*args, **kwargs):
    return


def log_info(*args, **kwargs):
    return


def log_error(*args, **kwargs):
    return


def get_cached_token(config):
    if config.cache_path is not None:
        return ""
    return None


def set_cached_token(config, auth_token):
    if config.cache_path is not None:
        return True
    return False


def http_get(config, url, headers):
    return None


def http_post(config, url, headers, data):
    return None

