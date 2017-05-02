#!/usr/bin/python3.6

if __name__ == "__main__":

    try:

        LOCAL_FOLDER_PATH = "/var/lib/CallerLookup"
        LOCAL_INI_PATH = LOCAL_FOLDER_PATH + "/CallerLookup.ini"

        import sys
        import os

        is_user_present = True
        for arg in sys.argv:
            if arg == "--silent":
                exit(0)

        from whiptailPy import Whiptail

        wt = Whiptail(title="Configuration", auto_exit=False)

        response = wt.confirm(msg="Do you want to save the Google Account credentials as part of the "
                                  "configuration?",
                              default="yes",
                              yes="Yes",
                              no="No")
        if response == False:
            exit(0)

        if os.path.isfile(LOCAL_INI_PATH):
            if not wt.confirm(msg="Do you want to overwrite the existing configuration?",
                              default="no",
                              yes="Yes",
                              no="No"):
                exit(0)

        wt.title = "Google Account"

        email = wt.prompt(
            msg="Email Address:",
            default="",
            password=False)
        if email is None:
            exit(0)

        password = wt.prompt(
            msg="Password:",
            default="",
            password=True)
        if password is None:
            exit(0)

        otp_secret = wt.prompt(msg="OTP Secret:", default="", password=False) \
            if wt.confirm(msg="Is Two Factor Authentication enabled?", default="Yo", yes="Yes", no="No") \
            else ""
        if otp_secret is None:
            exit(0)

        if not os.path.isdir(LOCAL_FOLDER_PATH):
            os.makedirs(LOCAL_FOLDER_PATH)

        with open(LOCAL_INI_PATH, "w+") as ini:
            ini.write("[Credentials]\n")
            ini.write("username = {0}\n".format(email))
            ini.write("password = {0}\n".format(password))
            ini.write("otpsecret = {0}\n".format(otp_secret))

        wt.title = "Configuration"
        wt.alert("Configuration Saved.")

        exit(0)

    finally:

        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        print("\033[92mConfiguration Complete.\033[0m")

