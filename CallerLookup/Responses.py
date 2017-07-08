from CallerLookup.Strings import CallerLookupLabel, CallerLookupKeys


def get_response_invalid(number, region):
    return {CallerLookupLabel.RESULT: CallerLookupLabel.INVALID_NUMBER,
            CallerLookupLabel.NUMBER: number,
            CallerLookupLabel.REGION: region}


def get_response_error(message):
    return {CallerLookupLabel.RESULT: CallerLookupLabel.ERROR,
            CallerLookupLabel.MESSAGE: message}


def get_response_success(data, start_time=None):
    from json import loads
    from time import time

    result = {CallerLookupLabel.RESULT: CallerLookupLabel.UNKNOWN,
              CallerLookupLabel.NUMBER: data[CallerLookupLabel.NUMBER_E164],
              CallerLookupLabel.REGION: data[CallerLookupLabel.REGION],
              CallerLookupLabel.SCORE: 100}

    data = loads(data)

    if CallerLookupKeys.KEY_DATA in data:
        data = data[CallerLookupKeys.KEY_DATA]

    if len(data) > 0:
        data = data[0]

    if CallerLookupKeys.KEY_SCORE in data:
        result[CallerLookupLabel.SCORE] = round(data[CallerLookupKeys.KEY_SCORE]
                                                * 100)

    if CallerLookupKeys.KEY_ADDRESSES in data:
        addresses = data[CallerLookupKeys.KEY_ADDRESSES]
        if len(addresses) > 0:
            if CallerLookupKeys.KEY_COUNTRY_CODE in addresses[0]:
                result[CallerLookupLabel.REGION] =\
                    addresses[0][CallerLookupKeys.KEY_COUNTRY_CODE].upper()
            if CallerLookupKeys.KEY_ADDRESS in addresses[0]:
                result[CallerLookupLabel.ADDRESS] = \
                    addresses[0][CallerLookupKeys.KEY_ADDRESS]

    if CallerLookupKeys.KEY_NAME in data:
        result[CallerLookupLabel.NAME] = data[CallerLookupKeys.KEY_NAME]
        result[CallerLookupLabel.RESULT] = CallerLookupLabel.SUCCESS

    if start_time is not None:
        elapsed = time() - start_time
        result[CallerLookupLabel.TIME_TAKEN] = round(elapsed, 5)

    return result
