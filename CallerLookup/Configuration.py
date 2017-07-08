class CallerLookupConfiguration(object):
    def __init__(self,
                 google_account_username=None,
                 google_account_password=None,
                 google_account_otp_secret=None,
                 phantomjs_path=None,
                 cookies_path=None,
                 cache_path=None,
                 is_debug=False,
                 image_path=None,
                 phantomjs_log_path=None):
        self.google_account_username = google_account_username
        self.google_account_password = google_account_password
        self.google_account_otp_secret = google_account_otp_secret
        self.phantomjs_path = phantomjs_path
        self.cookies_path = cookies_path
        self.cache_path = cache_path
        self.is_debug = is_debug
        self.image_path = image_path
        self.phantomjs_log_path = phantomjs_log_path
