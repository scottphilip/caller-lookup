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
import subprocess
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
    INTERPRETER_PYTHON_PATH = "#!{0}\n".format(sys.executable)

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

    is_user_present = True
    for arg in sys.argv:
        if arg == "--silent":
            is_user_present = False

    try:

        if not os.path.isdir(CallerLookupInstall.LOCAL_FOLDER_PATH):
            os.makedirs(CallerLookupInstall.LOCAL_FOLDER_PATH)

        if is_user_present:
            url = CallerLookupInstall.GITHUB_MASTER_URL + "/Install/Configure.py"
            path = os.path.expanduser("~") + "/Configure.py"
            CallerLookupInstall.print_update("Downloading {0} to {1} ...".format(url, path))
            CallerLookupInstall.download_file(url, path)
            subprocess.call([sys.executable, path])
            # if CallerLookupInstall.confirm("Do you want to save the Google Credentials in a configuration file?"):
            #
            #     config_username = CallerLookupInstall.get_input("Please enter Google Account Username:")
            #
            #     config_password = CallerLookupInstall.get_input("Please enter Google Account Password:")
            #
            #     config_otpsecret = CallerLookupInstall.get_input("If enabled, enter the One Time Passcode Secret "
            #                                                      "(Leave blank if not enabled):")
            #
            #     with open(CallerLookupInstall.LOCAL_FOLDER_PATH + "/CallerLookup.ini", "w+") as ini:
            #         ini.write("[Credentials]\n")
            #         ini.write("username = {0}\n".format(config_username))
            #         ini.write("password = {0}\n".format(config_password))
            #         ini.write("otpsecret = {0}\n".format(config_otpsecret))

        if not is_user_present or CallerLookupInstall.confirm("Do you want to install the required Python Packages?"):

            # import requests.cookies
            CallerLookupInstall.install_package("requests")

            # import selenium
            CallerLookupInstall.install_package("selenium")

            # import phonenumbers
            CallerLookupInstall.install_package("phonenumbers")

            # import pyotp
            CallerLookupInstall.install_package("pyotp")

            #import asterisk
            CallerLookupInstall.install_package("pyst2")

            # import configparser
            CallerLookupInstall.install_package("configparser")

            # import http
            CallerLookupInstall.install_package("http")

            # import argparse
            CallerLookupInstall.install_package("argparse")

            # import json
            CallerLookupInstall.install_package("json")

        CallerLookupInstall.print_update("Downloading CallerLookup Files ...")

        url = CallerLookupInstall.GITHUB_MASTER_URL + "/Python/CallerLookup.py"
        path = CallerLookupInstall.LOCAL_FOLDER_PATH + "/CallerLookup.py"
        CallerLookupInstall.download_file(url, path)
        CallerLookupInstall.set_interpreter(path)

        url = CallerLookupInstall.GITHUB_MASTER_URL + "/Python/CountryCodes.json"
        path = CallerLookupInstall.LOCAL_FOLDER_PATH + "/CountryCodes.json"
        CallerLookupInstall.download_file(url, path)

        # Asterisk Plugins
        if os.path.exists(CallerLookupInstall.ASTERISK_AGIBIN_PATH):

            url = CallerLookupInstall.GITHUB_MASTER_URL + "/Plugins/Asterisk/SetCallerIdName.agi"
            path = CallerLookupInstall.ASTERISK_AGIBIN_PATH + "/SetCallerIdName.agi"
            CallerLookupInstall.download_file(url, path)
            CallerLookupInstall.set_interpreter(path)

            url = CallerLookupInstall.GITHUB_MASTER_URL + "/Plugins/Asterisk/FormatCallerId.agi"
            path = CallerLookupInstall.ASTERISK_AGIBIN_PATH + "/FormatCallerId.agi"
            CallerLookupInstall.download_file(url, path)
            CallerLookupInstall.set_interpreter(path)

        # FreePBX Plugins
        if os.path.exists(CallerLookupInstall.SUPERFECTA_SOURCES_PATH):

            url = CallerLookupInstall.GITHUB_MASTER_URL + "/Plugins/FreePBX/source-CallerLookup.module.php"
            path = CallerLookupInstall.SUPERFECTA_SOURCES_PATH + "/sources-CallerLookup.module"
            CallerLookupInstall.download_file(url, path)

        exit(0)

    except Exception as e:

        print("{0}An error has occurred during setup.{1}{2}".format(C.FAIL, str(e), C.ENDC))
        exit(1)
