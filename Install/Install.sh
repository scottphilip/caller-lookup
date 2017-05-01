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
#  ARGS
#-----------------------------------------------------------------------------------------------
IS_USER_PRESENT=1
while [ "$1" != "" ]; do
    case $1 in
        -s | --silent )         IS_USER_PRESENT=0
                                RESPONSE="y"
                                ;;
        * )                     echo "Unknown flag provided."
                                exit 1
    esac
    shift
done
#-----------------------------------------------------------------------------------------------
#  SETUP
#-----------------------------------------------------------------------------------------------
RESPONSE=""
if [ "$EUID" -ne 0 ]
then
	printf "\033[0;31mThis must be run as root or with sudo.\033[0m\n"
    exit
fi

if [ "$IS_USER_PRESENT" == 1 ]
then
    printf "\033[0;33mAre you sure you want to install CallerLookup? [y/N] \033[0m\n"
    read -r RESPONSE
fi
case "$RESPONSE" in
    [yY][eE][sS]|[yY])
        ;;
    *)
        exit
        ;;
esac

#-----------------------------------------------------------------------------------------------
#  Discover Python Version
#-----------------------------------------------------------------------------------------------
PY_VERSION=""
if [ -n "$(command -v python2.7)" ]
then
    PY_VERSION="2.7"
fi
if [ -n "$(command -v python3)" ]
then
    PY_VERSION="3"
fi

#-----------------------------------------------------------------------------------------------
#  Install Python
#-----------------------------------------------------------------------------------------------
if [ "$PY_VERSION" == "" ]
then
    if [ "$IS_USER_PRESENT" == 1 ]
    then
        printf "\033[0;33mDo you want to download and install Python3.6? [y/N] \033[0m\n"
        read -r RESPONSE
    fi
    case "$RESPONSE" in
        [yY][eE][sS]|[yY])
            cd ~
            wget https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Install/Install-Python3.6.0.sh
            chmod +x Install-Python3.6.0.sh
            ./Install-Python3.6.0.sh
            ;;
        *)
            exit
            ;;
    esac
fi

#-----------------------------------------------------------------------------------------------
#  Setup.py
#-----------------------------------------------------------------------------------------------
cd ~
wget https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Install/Setup.py
chmod +x Setup.py
$(command -v python${PY_VERSION} Setup.py)

#-----------------------------------------------------------------------------------------------
#  FINISHED
#-----------------------------------------------------------------------------------------------
printf "\033[0;32mInstallation Complete.\033[0m\n"
exit 0




#mkdir /var/lib/CallerLookup
#-----------------------------------------------------------------------------------------------
#  DOWNLOAD SCRIPT FILES
#-----------------------------------------------------------------------------------------------
#printf "\033[0;32mSaving CallerLookup.py...\032[0m\n"
#wget -O /var/lib/CallerLookup/CallerLookup.py "${GITHUB_MASTER_URL}/Python/CallerLookup.py"
#chmod +x /var/lib/CallerLookup/CallerLookup.py
#printf "\033[0;32mSaving CountryCodes.json...\033[0m\n"
#wget -O /var/lib/CallerLookup/CountryCodes.json "${GITHUB_MASTER_URL}/Python/CountryCodes.json"
#printf "\033[0;32mSaving Asterisk AGI Component...\033[0m\n"
#wget -O "${ASTERISK_AGIBIN_PATH}/Asterisk-CallerLookup.py" "${GITHUB_MASTER_URL}/Plugins/Asterisk-CallerLookup.py"
#cd "${ASTERISK_AGIBIN_PATH}"
#chmod +x Asterisk-CallerLookup.py
#cd ~
#printf "\033[0;32mSaving Superfecta Module...\033[0m\n"
#wget -O "${SUPERFECTA_SOURCES_PATH}/source-CallerLookup.module" "${GITHUB_MASTER_URL}/Plugins/source-CallerLookup.module.php"


#-----------------------------------------------------------------------------------------------
#  CREATE SETTINGS INI FILE
#-----------------------------------------------------------------------------------------------
#if [ "$IS_USER_PRESENT" == 1 ]
#then
#    printf "\033[0;33mDo you want to save your Google Account Credentials in the config file? [y/N] \033[0m\n"
#    read -r RESPONSE
#    case "$RESPONSE" in
#        [yY][eE][sS]|[yY])
#            printf "\033[0;33mPlease enter your Google Account Username (Email): \033[0m\n"
#            read -r username
#            printf "\033[0;33mPlease enter your Google Account Password: \033[0m\n"
#            read -r -s password
#            printf "\033[0;33mIf 2-Step Verification is enabled, please enter TOTP secret: \033[0m\n"
#            read -r otpsecret
#            echo "[Credentials]" > "/var/lib/CallerLookup/CallerLookup.ini"
#            echo "username = $username" >> "/var/lib/CallerLookup/CallerLookup.ini"
#            echo "password = $password" >> "/var/lib/CallerLookup/CallerLookup.ini"
#            echo "otpsecret = $otpsecret" >> "/var/lib/CallerLookup/CallerLookup.ini"
#            printf "\033[0;32mCredentials Saved.\033[0m\n"
##            ;;
#   esac
#fi
#-----------------------------------------------------------------------------------------------
#  INSTALL PIP PACKAGES
#-----------------------------------------------------------------------------------------------
#install_pip_package() {
#    printf "\033[0;32mInstalling $1...\033[0m\n"
#    eval pip install $1
#}
#
#if [ "$IS_USER_PRESENT" == 1 ]
#then
#    printf "\033[0;33mDo you want to install Python2.7 packages from PIP? [y/N] \033[0m\n"
#    read -r RESPONSE
#fi
#case "$RESPONSE" in
#    [yY][eE][sS]|[yY])
#        source CallerLookupEnvironment/bin/activate

#        deactivate
#        exit
#        ;;
#    *)
#        exit
#        ;;
#esac
#-----------------------------------------------------------------------------------------------
#  FINISHED
#-----------------------------------------------------------------------------------------------
#printf "\033[0;32mInstallation Complete.\033[0m\n"
#exit 0
