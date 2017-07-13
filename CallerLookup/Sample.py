# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (13 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup import CallerLookup
from logging import getLogger, DEBUG, INFO, StreamHandler, Formatter


def demo():
    username = get_input("Google Account Email:")
    password = get_input("Google Account Password:")
    otp_secret = get_input("Google Account OTP Secret (Blank if none):")
    int_dial_code = get_input("International Dialling Code of the receiving line:")

    with CallerLookup(account_email=username,
                      account_password=password,
                      account_otp_secret=otp_secret) as caller_lookup:

        while True:
            search_number = get_input("Phone Number to search (Leave Blank to exit):")
            if search_number == "":
                return
            result = caller_lookup.search(search_number, int_dial_code=int_dial_code)
            print(str(result))


def get_input(prompt):
    try:
        return raw_input(prompt)
    except NameError:
        pass
    print(input(prompt))


if __name__ == "__main__":

    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser = ArgumentParser(description='Reverse Caller Id',
                            formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("--number", "--n",
                        nargs="+",
                        dest="phone_numbers",
                        help="Phone number accepted in any standard format. When not in international format, the \
                                      default region parameter must be supplied",
                        action='append', required=True)

    parser.add_argument("--dialcode", "--d",
                        dest="int_dial_code",
                        default="49",
                        help="The international dial code that the receieving trunk belongs to.  "
                             "Only required when phone number is supplied without an international "
                             "dialling code.",
                        required=False)

    parser.add_argument("--username", "--u",
                        help="Google Username",
                        dest="account_email",
                        required=True)

    parser.add_argument("--password", "--p",
                        help="Google Password - only required for first use",
                        dest="account_password",
                        required=False)

    parser.add_argument("--otp", "--o",
                        help="Google OTP Secret - only required for first use",
                        dest="account_otp_secret",
                        required=False)

    parser.add_argument("--debug",
                        help="Debug mode",
                        action="store_true",
                        dest="is_debug")

    args = vars(parser.parse_args())

    logger = getLogger("CallerLookup")
    logger.setLevel(DEBUG if args["is_debug"] else INFO)
    consoleHandler = StreamHandler()
    logger.addHandler(consoleHandler)

    caller_lookup = CallerLookup(account_email=args["account_email"],
                                 account_password=args["account_password"],
                                 account_otp_secret=args["account_otp_secret"],
                                 is_debug=args["is_debug"],
                                 logger=logger)

    for phone_number in args["phone_numbers"]:
        response = caller_lookup.search(" ".join(phone_number),
                                        int_dial_code=args["int_dial_code"])

        print(str(response))
