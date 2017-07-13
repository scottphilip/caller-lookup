# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (13 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from GoogleToken import GoogleTokenConfiguration
from CallerLookup.Strings import CallerLookupKeys
from os.path import join, expanduser, isdir
from os import makedirs


class CallerLookupConfiguration(GoogleTokenConfiguration):
    def __init__(self,
                 account_email=None,
                 account_password=None,
                 account_otp_secret=None,
                 cookie_storage_path=None,
                 logger=None,
                 phantomjs_path=None,
                 phantomjs_log_path=None,
                 image_path=None,
                 is_debug=False,
                 cache_path=None,
                 cache_folder_path=None):
        super(CallerLookupConfiguration, self).__init__(
            account_email=account_email,
            account_password=account_password,
            account_otp_secret=account_otp_secret,
            cookie_storage_path=cookie_storage_path,
            oauth_client_id=CallerLookupKeys.OAUTH2_CLIENT_ID,
            oauth_redirect_uri=CallerLookupKeys.OAUTH2_REDIRECT_URI,
            oauth_scope=CallerLookupKeys.OAUTH2_SCOPE,
            logger=logger,
            image_path=image_path,
            execute_script=CallerLookupKeys.GET_TOKEN_JAVASCRIPT,
            phantomjs_path=phantomjs_path,
            phantomjs_log_path = phantomjs_log_path
        )
        if cache_path is None:
            if not isdir(join(expanduser("~"), "CallerLookup")):
                makedirs(join(expanduser("~"), "CallerLookup"))
        self.cache_path = join(expanduser("~"), "CallerLookup", "tokens.txt") if cache_path is None else cache_path
        if cache_folder_path is None:
            if not isdir(join(expanduser("~"), "CallerLookup", "Cache")):
                makedirs(join(expanduser("~"), "CallerLookup", "Cache"))
        self.cache_folder_path = join(expanduser("~"), "CallerLookup", "Cache") if cache_folder_path is None else cache_folder_path
        self.is_debug = is_debug
