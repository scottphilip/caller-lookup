# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
from json import dumps, loads
from os.path import join, isfile
import re
from CallerLookup.CountryCodes import get_region_dial_code


def __cached_file_path(config, phone_number, region=None, region_dial_code=None):
    phone_number = re.sub("\D", "", phone_number)
    region_dial_code = get_region_dial_code(region) if region_dial_code is None else region_dial_code
    result = []
    if region_dial_code is not None and len(str(region_dial_code)) > 0:
        result.append(str(region_dial_code))
    result.append(phone_number)
    return join(config.get_cache_dir(), "_".join(result))


def get_cached_response(config, phone_number, region=None, region_dial_code=None):
    if not config.is_cache_enabled():
        return None
    file_path = __cached_file_path(config, phone_number, region, region_dial_code)
    if isfile(file_path):
        with open(file_path) as file:
            result = file.read()
            if result is not None and len(result) > 0:
                return loads(result)
    return None


def set_cached_response(config, phone_number, data):
    if not config.is_cache_enabled():
        return
    region_dial_code = data["REGION_DIAL_CODE"] if "REGION_DIAL_CODE" in data else None
    file_path = __cached_file_path(config, phone_number, region_dial_code=region_dial_code)
    with open(file_path, "w") as file:
        file.write(dumps(data))
