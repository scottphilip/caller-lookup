#!/bin/bash
#
# Usage:
#
#               wget https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Install-CentOS.sh
#               chmod +x Install-CentOS.sh
#               sudo ./Install-CentOS.sh
#
# Author:       Scott Philip (sp@scottphilip.com)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
#               CallerLookup Copyright (C) 2017 SCOTT PHILIP
#               This program comes with ABSOLUTELY NO WARRANTY
#               This is free software, and you are welcome to redistribute it
#               under certain conditions
#               https://github.com/scottphilip/caller-lookup/blob/master/LICENSE.md



#-----------------------------------------------------------------------------------------------
#  CONSTANTS
#-----------------------------------------------------------------------------------------------
GITHUB_MASTER_URL='https://raw.githubusercontent.com/scottphilip/caller-lookup/master'
SUPERFECTA_SOURCES_PATH='/var/www/html/admin/modules/superfecta/sources'
ASTERISK_AGIBIN_PATH='/var/lib/asterisk/agi-bin'



#-----------------------------------------------------------------------------------------------
#  ARGS
#-----------------------------------------------------------------------------------------------
IS_SILENT_INSTALL=0

function invalid_flag()
{
    echo "Unknown flag provided."
}

while [ "$1" != "" ]; do
    case $1 in
        -s | --silent )         IS_SILENT_INSTALL=1
                                ;;
        * )                     invalid_flag
                                exit 1
    esac
    shift
done

response="y"

#-----------------------------------------------------------------------------------------------
#  SETUP
#-----------------------------------------------------------------------------------------------
cd ~
if [ "$EUID" -ne 0 ]
then
	printf "\033[0;31mThis must be run as root or with sudo.\033[0m\n"
    exit
fi
if [ "$IS_SILENT_INSTALL" == 0 ]
then
    printf "\033[0;33mAre you sure you want to install CallerLookup? [y/N] \033[0m\n"
    read -r response
fi
case "$response" in
    [yY][eE][sS]|[yY])
        ;;
    *)
        exit
        ;;
esac
mkdir /var/lib/CallerLookup
cd ~


#-----------------------------------------------------------------------------------------------
#  DOWNLOAD SCRIPT FILES
#-----------------------------------------------------------------------------------------------
printf "\033[0;32mSaving CallerLookup.py...\032[0m\n"
wget -O /var/lib/CallerLookup/CallerLookup.py "${GITHUB_MASTER_URL}/Python/CallerLookup.py"
chmod +x /var/lib/CallerLookup/CallerLookup.py
printf "\033[0;32mSaving CountryCodes.json...\033[0m\n"
wget -O /var/lib/CallerLookup/CountryCodes.json "${GITHUB_MASTER_URL}/Python/CountryCodes.json"
printf "\033[0;32mSaving Asterisk AGI Component...\033[0m\n"
wget -O "${ASTERISK_AGIBIN_PATH}/Asterisk-CallerLookup.py" "${GITHUB_MASTER_URL}/Plugins/Asterisk-CallerLookup.py"
cd "${ASTERISK_AGIBIN_PATH}"
chmod +x Asterisk-CallerLookup.py
cd ~
printf "\033[0;32mSaving Superfecta Module...\033[0m\n"
wget -O "${SUPERFECTA_SOURCES_PATH}/source-CallerLookup.module" "${GITHUB_MASTER_URL}/Plugins/source-CallerLookup.module.php"


#-----------------------------------------------------------------------------------------------
#  CREATE SETTINGS INI FILE
#-----------------------------------------------------------------------------------------------
if [ "$IS_SILENT_INSTALL" == 0 ]
then
    printf "\033[0;33mDo you want to save your Google Account Credentials in the config file? [y/N] \033[0m\n"
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY])
            printf "\033[0;33mPlease enter your Google Account Username (Email): \033[0m\n"
            read -r username
            printf "\033[0;33mPlease enter your Google Account Password: \033[0m\n"
            read -r -s password
            printf "\033[0;33mIf 2-Step Verification is enabled, please enter TOTP secret: \033[0m\n"
            read -r otpsecret
            echo "[Credentials]" > "/var/lib/CallerLookup/CallerLookup.ini"
            echo "username = $username" >> "/var/lib/CallerLookup/CallerLookup.ini"
            echo "password = $password" >> "/var/lib/CallerLookup/CallerLookup.ini"
            echo "otpsecret = $otpsecret" >> "/var/lib/CallerLookup/CallerLookup.ini"
            printf "\033[0;32mCredentials Saved.\033[0m\n"
            ;;
    esac
fi


#-----------------------------------------------------------------------------------------------
#  INSTALL PYTHON2.7
#-----------------------------------------------------------------------------------------------
#TODO


#-----------------------------------------------------------------------------------------------
#  INSTALL PIP PACKAGES
#-----------------------------------------------------------------------------------------------
install_pip_package() {
    printf "\033[0;32mInstalling $1...\033[0m\n"
    eval pip install $1
}

if [ "$IS_SILENT_INSTALL" == 0 ]
then
    printf "\033[0;33mDo you want to install Python2.7 packages from PIP? [y/N] \033[0m\n"
    read -r response
fi
case "$response" in
    [yY][eE][sS]|[yY])
        source CallerLookupEnvironment/bin/activate
        install_pip_package selenium
        install_pip_package phonenumbers
        install_pip_package pyotp
        install_pip_package pyst2
        install_pip_package configparser
        install_pip_package http
        install_pip_package cookiejar
        install_pip_package parse
        install_pip_package requests
        deactivate
        exit
        ;;
    *)
        exit
        ;;
esac


#-----------------------------------------------------------------------------------------------
#  FINISHED
#-----------------------------------------------------------------------------------------------
printf "\033[0;32mInstallation Complete.\033[0m\n"
exit 0
