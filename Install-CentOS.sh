#!/bin/bash

cd /tmp

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

confirm() {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? [y/N]} " response
    case "$response" in
        [yY][eE][sS]|[yY])
            false
            ;;
        *)
            true
            ;;
    esac
}

#Check SUDO
if [ "$EUID" -ne 0 ]
then
	printf "${RED}This must be run as root or with sudo.${NC}\n"
    exit
fi

read -r -p "Are you sure you want to install CallerLookup? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
        ;;
    *)
        exit
        ;;
esac

read -r -p "Do you want to save your Google Acount Credentials in the config file? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])

        read -r -p "Please enter your Google Account Username (Email): " username
        read -r -p -s "Please enter your Google Account Password: " password
        read -r -p "If 2-Step Verification is enabled, please enter TOTP secret: " otpsecret

        echo "[Credentials]\n" > "/var/lib/CallerLookup/CallerLookup.ini"
        echo "username = $username\n" >> "/var/lib/CallerLookup/CallerLookup.ini"
        echo "password = $password\n" >> "/var/lib/CallerLookup/CallerLookup.ini"
        echo "otpsecret = $otpsecret\n" >> "/var/lib/CallerLookup/CallerLookup.ini"

        ;;
esac

printf "${GREEN}Adding Source...${NC}\n"
/usr/bin/yum -y install https://centos7.iuscommunity.org/ius-release.rpm

printf "${GREEN}Updating Packages...${NC}\n"
/usr/bin/yum update

printf "${GREEN}Python...${NC}\n"
wget http://python.org/ftp/python/3.6.0/Python-3.6.0.tar.xz
tar xf Python-3.6.0.tar.xz
cd Python-3.6.0
./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
make && make altinstall

printf "${GREEN}Python PIP...${NC}\n"
wget https://bootstrap.pypa.io/get-pip.py
python3.6 get-pip.py

printf "${GREEN}Selenium...${NC}\n"
/usr/local/bin/pip install selenium

printf "${GREEN}PhoneNumbers...${NC}\n"
/usr/local/bin/pip install phonenumbers

printf "${GREEN}Pyotp...${NC}\n"
/usr/local/bin/pip install pyotp

mkdir /var/lib/CallerLookup

printf "${GREEN}Saving CallerLookup.py...${NC}\n"
wget -O /var/lib/CallerLookup/CallerLookup.py https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Python/CallerLookup.py

printf "${GREEN}Saving CountryCodes.json...${NC}\n"
wget -O /var/lib/CallerLookup/CountryCodes.json https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Python/CountryCodes.json

printf "${GREEN}Saving Asterisk AGI Component...${NC}\n"
wget -O /var/lib/asterisk/agi-bin/Asterisk-CallerLookup.py https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Plugins/Asterisk-CallerLookup.py

printf "${GREEN}Saving Superfecta Module...${NC}\n"
wget -O /var/www/html/admin/modules/superfecta/sources/source-CallerLookup.module https://raw.githubusercontent.com/scottphilip/caller-lookup/master/Plugins/source-CallerLookup.module.php

printf "${YELLOW}Complete.${NC}\n"

exit