from CallerLookup.Utils import *


def get_search_response_data(config, number_data):
    auth_token = get_auth_token(config)
    return ""


def get_auth_token(config):
    auth_token = get_cached_token(config)
    if auth_token is None:
        google_token = get_google_token()
        auth_token = "123"
        set_cached_token(config, auth_token)
    return auth_token


def get_google_token(config):
    from GoogleToken import GoogleTokenGenerator, GoogleTokenParameters
    token_generator = GoogleTokenGenerator(
        params=GoogleTokenParameters(
            account_email=config.google_account_username,
            account_password=config.google_account_password,
            account_otp_secret=config.google_account_otp_secret))
    return token_generator.generate()






