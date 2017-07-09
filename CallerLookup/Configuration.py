# Author:       Scott Philip (sp@scottphilip.com)
# Version:      0.1 (10 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from GoogleToken import GoogleTokenParameters
from CallerLookup.Strings import CallerLookupKeys


class CallerLookupConfiguration(GoogleTokenParameters):
    def __init__(self,
                 account_email=None,
                 account_password=None,
                 account_otp_secret=None,
                 cookies_path=None,
                 cache_path=None,
                 logger=None,
                 is_debug=False,
                 image_path=None,
                 phantomjs_path=None,
                 phantomjs_log_path=None):
        super(CallerLookupConfiguration, self).__init__(
            account_email=account_email,
            account_password=account_password,
            account_otp_secret=account_otp_secret,
            cookie_storage_path=cookies_path,
            oauth_client_id=CallerLookupKeys.OAUTH2_CLIENT_ID,
            oauth_redirect_uri=CallerLookupKeys.OAUTH2_REDIRECT_URI,
            oauth_scope=CallerLookupKeys.OAUTH2_SCOPE,
            logger=logger,
            image_path=image_path,
            execute_script=CallerLookupKeys.GET_TOKEN_JAVASCRIPT)
        self.cache_path = cache_path
        self.is_debug = is_debug
        self.phantomjs_path = phantomjs_path
        self.phantomjs_log_path = phantomjs_log_path
