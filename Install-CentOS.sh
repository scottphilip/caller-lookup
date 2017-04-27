#!/bin/bash

cd /tmp

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

#Check SUDO
if [ "$EUID" -ne 0 ]
then
	printf "${RED}This must be run as root or with sudo.{NC}\n"
    exit
fi

read -r -p "Are you sure you want to install CallerLookup and its dependencies? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
        printf "${GREEN}Starting installation...{NC}\n"
        ;;
    *)
        exit
        ;;
esac

printf "${GREEN}Updating Packages...{NC}\n"
/usr/bin/yum update

printf "${GREEN}Python 3.6...{NC}\n"
/usr/bin/yum install python36u

printf "${GREEN}Python PIP 3.6...{NC}\n"
/usr/bin/yum install python36u-pip

printf "${GREEN}Selenium...{NC}\n"
/usr/bin/pip install selenium

printf "${GREEN}PhoneNumbers...{NC}\n"
/usr/bin/pip install phonenumbers

printf "${GREEN}Pyotp...{NC}\n"
/usr/bin/pip install pyotp

printf "${GREEN}Saving Asterisk AGI Component...{NC}\n"
wget -O Asterisk-CallerLookup.py https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Plugins/Asterisk-CallerLookup.py
mv Asterisk-CallerLookup.py /var/lib/asterisk/agi-bin/Asterisk-CallerLookup.py

printf "${GREEN}Saving Superfecta Module...{NC}\n"
wget -O source-CallerLookup.module https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Plugins/source-CallerLookup.module.php
mv source-CallerLookup.module /var/www/html/admin/modules/superfecta/sources/source-CallerLookup.module

printf "${GREEN}Complete.{NC}\n"