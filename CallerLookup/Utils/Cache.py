# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
from json import dumps, loads
from os.path import join, isfile


def get_cached_response(config, phone_number, region=None, region_dial_code=None):
    if not config.is_cache_enabled():
        return None
    import re
    phone_number = re.sub("\D", "", phone_number)
    file_path = join(config.get_cache_dir(), phone_number)
    if isfile(file_path):
        with open(file_path) as file:
            result = file.read()
            if result is not None and len(result) > 0:
                return loads(result)
    return None


def set_cached_response(config, phone_number, data, region=None, region_dial_code=None):
    if not config.is_cache_enabled():
        return
    import re
    phone_number = re.sub("\D", "", phone_number)
    file_path = join(config.get_cache_dir(), phone_number)
    with open(file_path, "w") as file:
        file.write(dumps(data))
