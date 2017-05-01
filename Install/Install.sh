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
RESPONSE=""
while [ "$1" != "" ]; do
    case $1 in
        -s | --silent )         IS_USER_PRESENT=0
                                RESPONSE="y"
                                ;;
        * )                     echo "Unknown flag provided."
                                exit 3
    esac
    shift
done
#-----------------------------------------------------------------------------------------------
#  SETUP
#-----------------------------------------------------------------------------------------------
if [ "$EUID" -ne 0 ]
then
	printf "\033[0;31mThis must be run as root or with sudo.\033[0m\n"
    exit 2
fi
if [ ${IS_USER_PRESENT} == 1 ]
then
    printf "\033[0;33mAre you sure you want to install CallerLookup? [y/N] \033[0m\n"
    read -r RESPONSE
fi
case ${RESPONSE} in
    [yY][eE][sS]|[yY])
        ;;
    *)
        exit 1
        ;;
esac

#-----------------------------------------------------------------------------------------------
#  Discover Python Version
#-----------------------------------------------------------------------------------------------
IS_PYTHON3_INSTALLED=0
PY_VERSION=""
if [ -n "$(command -v python)" ]
then
    VERSION="$(python -c 'import sys; print(sys.version_info[0])')"
    if [ ${VERSION} == "3" ]
    then
        IS_PYTHON3_INSTALLED=1
    fi
else
    if [ -n "$(command -v python3)" ]
    then
        PY_VERSION="3"
        IS_PYTHON3_INSTALLED=1
    fi
fi


#-----------------------------------------------------------------------------------------------
#  Install Python
#-----------------------------------------------------------------------------------------------
if [ ${IS_PYTHON3_INSTALLED} == 0 ]
then
    if [ ${IS_USER_PRESENT} == 1 ]
    then
        printf "\033[0;33mCannot find Python3 which is required to continue.  Do you want to download and install Python 3.6.1? [y/N] \033[0m\n"
        read -r RESPONSE
    fi
    case ${RESPONSE} in
        [yY][eE][sS]|[yY])
            cd ~
            wget -q https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Install/Install-Python3.6.1.sh -O Install-Python3.6.1.sh
            chmod +x Install-Python3.6.1.sh
            ./Install-Python3.6.1.sh
            if [ $? -eq 0 ]
            then
                IS_PYTHON3_INSTALLED=1
            fi
            ;;
        *)
            exit 1
            ;;
    esac
fi

#-----------------------------------------------------------------------------------------------
#  Setup.py
#-----------------------------------------------------------------------------------------------
if [ ${IS_PYTHON3_INSTALLED} == 1 ]
then
    cd ~
    wget https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Install/Setup.py
    chmod +x Setup.py
    $(command -v python${PY_VERSION} Setup.py)
fi

#-----------------------------------------------------------------------------------------------
#  FINISH
#-----------------------------------------------------------------------------------------------
printf "\033[0;32mInstallation Complete.\033[0m\n"
exit 0
