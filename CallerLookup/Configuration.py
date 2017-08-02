# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from os.path import join, isdir, isfile, dirname
from os import makedirs
from appdirs import AppDirs
from datetime import datetime, timedelta
from configparser import RawConfigParser
from CallerLookup.Strings import CallerLookupConfigStrings, CallerLookupKeys, CallerLookupReportMode
from CallerLookup.Utils.Logs import *
from GoogleToken.Crypto import encrypt as encrypt_value, decrypt as decrypt_value


def __get_value(str_value):
    if str_value is None:
        return None
    if not str_value:
        return None
    if str(str_value).upper() == "TRUE":
        return True
    if str(str_value).upper() == "FALSE":
        return False
    try:
        int_value = int(str_value)
        return int_value
    except:
        ignore = True
    return str_value


def _find_entry(key, items):
    for item in items:
        if item.upper() == key.upper():
            return items[item]
    return None


def _pop_entry(key, default, **kwargs):
    for a in kwargs:
        if key.upper() == a.upper():
            return kwargs.pop(a)
    return default


def __make_dir(config, path):
    if not isdir(str(path)):
        try:
            makedirs(str(path))
        except Exception as ex:
            log_error(config, "MAKE_DIR_ERROR", str(ex))


def __get_config_file_path(self):
    return join(self.config_dir, "{0}.ini".format(CallerLookupKeys.APP_NAME))


def encrypt(config, value, current_account):
    return encrypt_value(value, current_account, config.data_dir, config.logger)


def decrypt(config, value, current_account):
    return decrypt_value(value, current_account, config.data_dir, config.logger)


_DEFAULT_TEMPLATE = {
    CallerLookupConfigStrings.ACCOUNT: ""
}

_GENERAL_TEMPLATE = {
    CallerLookupConfigStrings.PHANTOMJS_PATH: "phantomjs",
    CallerLookupConfigStrings.IS_CACHE_ENABLED: True,
    CallerLookupConfigStrings.IS_DEBUG: False,
    CallerLookupConfigStrings.SMTP_SERVER: "localhost",
}

_REPORT_TEMPLATE = {
    CallerLookupConfigStrings.IS_REPORT_ENABLED: False,
    CallerLookupConfigStrings.REPORT_EMAIL_FROM: "noreply@domain.com",
    CallerLookupConfigStrings.REPORT_RECIPIENTS: "",
    CallerLookupConfigStrings.LAST_UTC: "2000-01-01 00:00:00",
    CallerLookupConfigStrings.NEXT_UTC: "2000-01-01 00:00:00",
    CallerLookupConfigStrings.SEND_MODE: CallerLookupReportMode.EVERY_DAY
}

_ACCOUNT_TEMPLATE = {
    CallerLookupConfigStrings.ACCESS_TOKEN: "",
    CallerLookupConfigStrings.ACCESS_TOKEN_EXPIRY: "2000-01-01 00:00:00",
    CallerLookupConfigStrings.USERNAME: "",
    CallerLookupConfigStrings.PASSWORD: "",
    CallerLookupConfigStrings.SECRET: ""
}

_TEMPLATE = {
    CallerLookupConfigStrings.DEFAULT: _DEFAULT_TEMPLATE,
    CallerLookupConfigStrings.GENERAL: _GENERAL_TEMPLATE,
    CallerLookupConfigStrings.REPORT: _REPORT_TEMPLATE
}

_RUNTIME = {
    CallerLookupConfigStrings.IS_SAVE_CREDENTIALS: True,
    CallerLookupConfigStrings.REMOVE_ACCOUNT: None,
    CallerLookupConfigStrings.SET_DEFAULT: None,
}

__ENCRYPT = [
    CallerLookupConfigStrings.PASSWORD,
    CallerLookupConfigStrings.SECRET,
    CallerLookupConfigStrings.ACCESS_TOKEN
]

__VALID_ARGUMENTS = [
    CallerLookupConfigStrings.NUMBER,
    CallerLookupConfigStrings.REGION,
    CallerLookupConfigStrings.REGION_DIAL_CODE,
    CallerLookupConfigStrings.PHANTOMJS_PATH,
    CallerLookupConfigStrings.IS_CACHE_ENABLED,
    CallerLookupConfigStrings.IS_DEBUG,
    CallerLookupConfigStrings.USERNAME,
    CallerLookupConfigStrings.PASSWORD,
    CallerLookupConfigStrings.SECRET,
    CallerLookupConfigStrings.IS_SAVE_CREDENTIALS,
    CallerLookupConfigStrings.REMOVE_ACCOUNT,
    CallerLookupConfigStrings.SET_DEFAULT,
    CallerLookupConfigStrings.CONFIG_DIR,
    CallerLookupConfigStrings.DATA_DIR,
    CallerLookupConfigStrings.LOG_DIR
]

__ARG_KEYS = {
    CallerLookupConfigStrings.NUMBER: ["number", "number"],
    CallerLookupConfigStrings.REGION: ["region", "trunk_region"],
    CallerLookupConfigStrings.REGION_DIAL_CODE: ["code", "trunk_code"],
    CallerLookupConfigStrings.PHANTOMJS_PATH: ["phantom", "path_to_phantom_js"],
    CallerLookupConfigStrings.IS_CACHE_ENABLED: ["cache", "cache_enabled"],
    CallerLookupConfigStrings.IS_DEBUG: ["debug", "debug_enabled"],
    CallerLookupConfigStrings.USERNAME: ["username", "username"],
    CallerLookupConfigStrings.PASSWORD: ["password", "password"],
    CallerLookupConfigStrings.SECRET: ["secret", "otp_secret"],
    CallerLookupConfigStrings.IS_SAVE_CREDENTIALS: ["savecred", "save_credentials"],
    CallerLookupConfigStrings.REMOVE_ACCOUNT: ["remove", "remove_account"],
    CallerLookupConfigStrings.SET_DEFAULT: ["default", "default_account_username"],
    CallerLookupConfigStrings.CONFIG_DIR: ["config", "path_to_config_directory"],
    CallerLookupConfigStrings.DATA_DIR: ["data", "path_to_data_directory"],
    CallerLookupConfigStrings.LOG_DIR: ["log", "path_to_log_directory"]
}

__DEFAULT_ARGS = {
    CallerLookupConfigStrings.IS_SAVE_CREDENTIALS: _RUNTIME[CallerLookupConfigStrings.IS_SAVE_CREDENTIALS],
    CallerLookupConfigStrings.IS_DEBUG: _GENERAL_TEMPLATE[CallerLookupConfigStrings.IS_DEBUG],
    CallerLookupConfigStrings.IS_CACHE_ENABLED: _GENERAL_TEMPLATE[CallerLookupConfigStrings.IS_CACHE_ENABLED],
    CallerLookupConfigStrings.PHANTOMJS_PATH: _GENERAL_TEMPLATE[CallerLookupConfigStrings.PHANTOMJS_PATH],
}


def _is_cache_enabled(config):
    if CallerLookupConfigStrings.GENERAL in config.settings:
        if CallerLookupConfigStrings.IS_CACHE_ENABLED in config.settings[CallerLookupConfigStrings.GENERAL]:
            return config.settings[CallerLookupConfigStrings.GENERAL][CallerLookupConfigStrings.IS_CACHE_ENABLED]
    log_info(config, "CONFIG", "MISSING GENERAL/is_cache_enabled property")
    return True


def _get_cached_token(config):
    if CallerLookupConfigStrings.ACCESS_TOKEN_EXPIRY in config.settings[config.account]:
        if datetime.strptime(config.settings[config.account][CallerLookupConfigStrings.ACCESS_TOKEN_EXPIRY],
                             CallerLookupKeys.DATETIME_FMT) > datetime.utcnow():
            if CallerLookupConfigStrings.ACCESS_TOKEN in config.settings[config.account]:
                result = config.settings[config.account][CallerLookupConfigStrings.ACCESS_TOKEN]
                if result and len(str(result)) > 0:
                    return result
    return None


def _clear_cached_token(config):
    if config.account in config.settings:
        config.settings[config.account][CallerLookupConfigStrings.ACCESS_TOKEN] = ""
        config.settings[config.account][CallerLookupConfigStrings.ACCESS_TOKEN_EXPIRY] = "2000-01-01 00:00:00"
    config.save()


def _set_cached_token(self, auth_token):
    self.settings.update({
        self.account: {
            CallerLookupConfigStrings.ACCESS_TOKEN: auth_token,
            CallerLookupConfigStrings.ACCESS_TOKEN_EXPIRY: (datetime.utcnow() + timedelta(seconds=3600)).strftime(
                CallerLookupKeys.DATETIME_FMT),
        }
    })
    self.save()


def _is_debug(config):
    return config.settings[CallerLookupConfigStrings.GENERAL][CallerLookupConfigStrings.IS_DEBUG]


def _init_logger(self, **kwargs):
    arg_is_debug = _find_entry(CallerLookupConfigStrings.IS_DEBUG, kwargs)
    if self.logger is None and arg_is_debug is True:
        from logging import getLogger, DEBUG, FileHandler, Formatter
        file_handler = FileHandler(join(str(self.log_dir), "CallerLookup.log"))
        file_handler.setFormatter(Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"))
        self.logger = getLogger(CallerLookupKeys.APP_NAME)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(file_handler)


def _init_config_runtime(self, **kwargs):
    is_updated = False
    config_file = RawConfigParser()
    config_file.optionxform = str
    config_file.read(__get_config_file_path(self))
    for runtime_setting_name in self.runtime:
        self.runtime[runtime_setting_name] = _pop_entry(runtime_setting_name,
                                                        self.runtime[runtime_setting_name],
                                                        **kwargs)
    if self.runtime[CallerLookupConfigStrings.REMOVE_ACCOUNT]:
        if self.runtime[CallerLookupConfigStrings.REMOVE_ACCOUNT] in self.settings:
            del self.settings[self.runtime[CallerLookupConfigStrings.REMOVE_ACCOUNT]]
        if self.runtime[CallerLookupConfigStrings.REMOVE_ACCOUNT] in config_file:
            del config_file[self.runtime[CallerLookupConfigStrings.REMOVE_ACCOUNT]]
        is_updated = True
    if self.runtime[CallerLookupConfigStrings.SET_DEFAULT]:
        if self.runtime[CallerLookupConfigStrings.SET_DEFAULT] not in config_file:
            raise Exception("Cannot set default to account that does not exist")
        config_file[CallerLookupConfigStrings.DEFAULT][CallerLookupConfigStrings.ACCOUNT] = \
            self.runtime[CallerLookupConfigStrings.SET_DEFAULT]
        is_updated = True
    if is_updated:
        if config_file is not None:
            with open(__get_config_file_path(self), "w") as file:
                config_file.write(file)


def _init_config(self, **kwargs):
    config_file = RawConfigParser()
    config_file.optionxform = str
    config_file.read(__get_config_file_path(self))
    self.account = _find_entry(CallerLookupConfigStrings.USERNAME, kwargs)
    if self.account is None and CallerLookupConfigStrings.DEFAULT in config_file:
        if CallerLookupConfigStrings.ACCOUNT in config_file[CallerLookupConfigStrings.DEFAULT]:
            self.account = config_file[CallerLookupConfigStrings.DEFAULT][CallerLookupConfigStrings.ACCOUNT]
    if not self.account:
        raise Exception("Unable to determine account")
    self.account = self.account.upper()
    self.settings = _TEMPLATE
    self.settings.update({self.account: _ACCOUNT_TEMPLATE})
    for section_name in self.settings:
        if section_name in config_file:
            for setting_name in self.settings[section_name]:
                if setting_name in config_file[section_name]:
                    value = config_file[section_name][setting_name]
                    if setting_name in __ENCRYPT:
                        value = decrypt(self, value, section_name)
                    self.settings[section_name][setting_name] = __get_value(value)
    for key in kwargs.keys():
        if key.upper() in _DEFAULT_TEMPLATE:
            self.settings[CallerLookupConfigStrings.DEFAULT][key.upper()] = kwargs[key]
        elif key.upper() in _GENERAL_TEMPLATE:
            self.settings[CallerLookupConfigStrings.GENERAL][key.upper()] = kwargs[key]
        elif key.upper() in _ACCOUNT_TEMPLATE:
            if self.runtime[CallerLookupConfigStrings.IS_SAVE_CREDENTIALS]:
                self.settings[self.account][key.upper()] = kwargs[key]


def _init_dirs(self, config_dir, data_dir, log_dir):
    d = AppDirs()
    self.config_dir = join(AppDirs().site_config_dir,
                           CallerLookupKeys.APP_NAME) if config_dir is None else config_dir
    self.data_dir = join(d.site_data_dir, CallerLookupKeys.APP_NAME) if data_dir is None else data_dir
    self.log_dir = join(d.user_log_dir, CallerLookupKeys.APP_NAME) if log_dir is None else log_dir
    __make_dir(self, self.config_dir)
    __make_dir(self, self.data_dir)
    __make_dir(self, self.log_dir)


def _save(self):
    self.settings[CallerLookupConfigStrings.DEFAULT][CallerLookupConfigStrings.ACCOUNT] = self.account \
        if not self.settings[CallerLookupConfigStrings.DEFAULT][CallerLookupConfigStrings.ACCOUNT] else \
        self.settings[CallerLookupConfigStrings.DEFAULT][CallerLookupConfigStrings.ACCOUNT]
    config_file = RawConfigParser()
    config_file.optionxform = str
    config_file.read(__get_config_file_path(self))
    for section_name in self.settings:
        if section_name not in config_file:
            config_file.add_section(section_name)
        for setting_name in self.settings[section_name]:
            if self.settings[section_name][setting_name] is not None:
                value = str(self.settings[section_name][setting_name])
                if setting_name in __ENCRYPT:
                    value = encrypt(self, value, section_name)
                config_file[section_name][setting_name] = str(value)
    with open(__get_config_file_path(self), "w") as file:
        config_file.write(file)


def _get_cache_dir(self):
    result = join(self.data_dir, "Cache")
    if not isdir(result):
        makedirs(result)
    return result


class CallerLookupConfiguration(object):
    account = None
    config_dir = None
    data_dir = None
    log_dir = None
    logger = None

    settings = {}
    runtime = _RUNTIME

    def __init__(self, **kwargs):
        _init_dirs(self,
                   config_dir=_pop_entry(CallerLookupConfigStrings.CONFIG_DIR, None, **kwargs),
                   data_dir=_pop_entry(CallerLookupConfigStrings.DATA_DIR, None, **kwargs),
                   log_dir=_pop_entry(CallerLookupConfigStrings.LOG_DIR, None, **kwargs))
        _init_logger(self, **kwargs)
        _init_config_runtime(self, **kwargs)
        _init_config(self, **kwargs)

    get_cached_token = _get_cached_token
    get_cache_dir = _get_cache_dir
    clear_cached_token = _clear_cached_token
    set_cached_token = _set_cached_token
    save = _save
    is_debug = _is_debug
    is_cache_enabled = _is_cache_enabled


def get_argument_parser():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    from CallerLookup.Strings import CallerLookupArgParserHelp as s

    parser = ArgumentParser(description=s.DESCRIPTION,
                            formatter_class=RawDescriptionHelpFormatter)

    for entry in __VALID_ARGUMENTS:
        arg_default_value = __DEFAULT_ARGS[entry] if entry in __DEFAULT_ARGS else None
        parser.add_argument("--{0}".format(__ARG_KEYS[entry][0]),
                            metavar=__ARG_KEYS[entry][1].upper(),
                            dest=entry,
                            type=type(arg_default_value) if arg_default_value else None,
                            help=getattr(s, entry, "") + (
                                " (Default: {0})".format(arg_default_value) if arg_default_value else ""),
                            default=arg_default_value,
                            required=False)

    return parser


def extract_values(items, **kwargs):
    results = {}
    for item in items:
        results.update({item: _pop_entry(item, None, **kwargs)})
    return results
