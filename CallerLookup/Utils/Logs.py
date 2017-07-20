# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (20 July 2017)
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
