# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)


def log_debug(config, *args, **kwargs):
    if config is not None and config.logger is not None:
        config.logger.debug(["CALLER_LOOKUP", args], **kwargs)


def log_info(config, *args, **kwargs):
    if config is not None and config.logger is not None:
        config.logger.info(["CALLER_LOOKUP", args], **kwargs)


def log_error(config, *args, **kwargs):
    if config is not None and config.logger is not None:
        config.logger.error(["CALLER_LOOKUP", args], **kwargs)


def format_exception(ex):
    if ex is None:
        return "ERROR"
    try:
        if ex.args is not None:
            if len(ex.args) >= 1:
                result = ""
                for item in ex.args:
                    result += (", " if len(result) > 0 else "") + str(item)
                return result
    except:
        ignore=True
    return type(ex).__name__
