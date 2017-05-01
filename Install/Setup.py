#!/usr/bin/python3
#
# Author:       Scott Philip (sp@scottphilip.com)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
#               CallerLookup Copyright (C) 2017 SCOTT PHILIP
#               This program comes with ABSOLUTELY NO WARRANTY
#               This is free software, and you are welcome to redistribute it
#               under certain conditions
#               https://github.com/scottphilip/caller-lookup/blob/master/LICENSE.md
import sys
assert sys.version_info >= (3,0,0)
import os
import sys
import stat
import pip
import urllib
import urllib.request

class C:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

class CallerLookupInstall:

    LOCAL_FOLDER_PATH = "/var/lib/CallerLookup"
    GITHUB_MASTER_URL = "https://raw.githubusercontent.com/scottphilip/caller-lookup/master"
    SUPERFECTA_SOURCES_PATH = "/var/www/html/admin/modules/superfecta/sources"
    ASTERISK_AGIBIN_PATH = "/var/lib/asterisk/agi-bin"
    INTERPRETER_PYTHON_PATH = "#!{0}".format(sys.executable)

    @staticmethod
    def install_package(package_name):
        CallerLookupInstall.print_update("Installing {0} ...".format(package_name))
        pip.main(["install", package_name])

    @staticmethod
    def confirm(message):
        if CallerLookupInstall.get_input("{0} [Y/n]".format(message)).upper().startswith("Y"):
            return True
        return False

    @staticmethod
    def get_input(message):
        print("{0}{1}{2}\n".format(C.OKBLUE, message, C.ENDC))
        return input()

    @staticmethod
    def print_update(message):
        print("{0}{1}{2}\n".format(C.OKGREEN, message, C.ENDC))

    @staticmethod
    def set_interpreter(file_path):
        with open(file_path) as fin:
            lines = fin.readlines()
        lines[0] = CallerLookupInstall.INTERPRETER_PYTHON_PATH
        with open(file_path, "w") as fout:
            for line in lines:
                fout.write(line)
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC)

    @staticmethod
    def download_file(file_url, file_path):
        with urllib.request.urlopen(file_url) as response, open(file_path, "wb") as out_file:
            data = response.read()
            out_file.write(data)


if __name__ == "__main__":

    try:

        os.makedirs(CallerLookupInstall.LOCAL_FOLDER_PATH)

        if CallerLookupInstall.confirm("Do you want to save the Google Credentials in a configuration file?"):

            config_username = CallerLookupInstall.get_input("Please enter Google Account Username:")

            config_password = CallerLookupInstall.get_input("Please enter Google Account Password:")

            config_otpsecret = CallerLookupInstall.get_input("If enabled, enter the One Time Passcode Secret "
                                                             "(Leave blank if not enabled):")

            with open(CallerLookupInstall.LOCAL_FOLDER_PATH + "/CallerLookup.ini", "w+") as ini:
                ini.write("[Credentials]\n")
                ini.write("username = {0}\n".format(config_username))
                ini.write("password = {0}\n".format(config_password))
                ini.write("otpsecret = {0}\n".format(config_otpsecret))

        if CallerLookupInstall.confirm("Do you want to install the required Python Packages?"):

            CallerLookupInstall.install_package("urllib")
            CallerLookupInstall.install_package("selenium")
            CallerLookupInstall.install_package("phonenumbers")
            CallerLookupInstall.install_package("pyotp")
            CallerLookupInstall.install_package("pyst2")
            CallerLookupInstall.install_package("configparser")
            CallerLookupInstall.install_package("http")
            CallerLookupInstall.install_package("cookiejar")
            CallerLookupInstall.install_package("parse")
            CallerLookupInstall.install_package("requests")

        CallerLookupInstall.print_update("Downloading CallerLookup Files ...")

        url = CallerLookupInstall.GITHUB_MASTER_URL + "/Python/CallerLookup.py"
        path = CallerLookupInstall.LOCAL_FOLDER_PATH + "/CallerLookup.py"
        CallerLookupInstall.download_file(url, path)
        CallerLookupInstall.set_interpreter(path)

        url = CallerLookupInstall.GITHUB_MASTER_URL + "/Python/CountryCodes.json"
        path = CallerLookupInstall.LOCAL_FOLDER_PATH + "/CountryCodes.json"
        CallerLookupInstall.download_file(url, path)

        if os.path.exists(CallerLookupInstall.ASTERISK_AGIBIN_PATH):
            url = CallerLookupInstall.GITHUB_MASTER_URL + "/Plugins/AsteriskAGI-SetCIDName.py"
            path = CallerLookupInstall.ASTERISK_AGIBIN_PATH + "/AsteriskAGI-SetCIDName.py"
            CallerLookupInstall.download_file(url, path)
            CallerLookupInstall.set_interpreter(path)


        if os.path.exists(CallerLookupInstall.SUPERFECTA_SOURCES_PATH):
            url = CallerLookupInstall.GITHUB_MASTER_URL + "/Plugins/source-CallerLookup.module.php"
            path = CallerLookupInstall.SUPERFECTA_SOURCES_PATH + "/sources-CallerLookup.module"
            CallerLookupInstall.download_file(url, path)

        exit(0)

    except Exception as e:

        print("{0}An error has occurred during setup.{1}{2}".format(C.FAIL, str(e), C.ENDC))
        exit(1)

