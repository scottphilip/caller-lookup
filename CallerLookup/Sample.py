# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup.Main import CallerLookup


def sample_1():
    """
        Creates search whilst encrypting and saving credentials to the config
    """

    username = get_input("Google Account Email:")
    password = get_input("Google Account Password:")
    otp_secret = get_input("Google Account OTP Secret (Blank if none):")
    region_dial_code = get_input("International Dialling Code of the receiving line:")

    with CallerLookup(account_email=username,
                      account_password=password,
                      account_otp_secret=otp_secret) as caller_lookup:

        while True:
            search_number = get_input("Phone Number to search (Leave Blank to exit):")
            if search_number == "":
                return
            result = caller_lookup.search(search_number, region_dial_code=region_dial_code)
            print(str(result))


def sample_2():
    """
        Uses credentials saved by sample 1.
    """

    with CallerLookup() as caller_lookup:
        search_number = get_input("Phone Number to search:")
        int_dial_code = get_input("International Dialling Code of the receiving line:")

        result = caller_lookup.search(search_number, region_dial_code=int_dial_code)
        print(str(result))


def get_input(prompt):
    try:
        return raw_input(prompt)
    except NameError:
        pass
    print(input(prompt))


if __name__ == "__main__":
    from CallerLookup import lookup_number
    import CallerLookup.Configuration

    parser = CallerLookup.Configuration.get_argument_parser()
    args = vars(parser.parse_args())
    response = lookup_number(**args)
    print(str(response))
