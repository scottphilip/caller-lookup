#!/bin/bash

################################################################################################
## CONSTANTS ###################################################################################
################################################################################################
GITHUB_MASTER_URL='https://raw.githubusercontent.com/scottphilip/caller-lookup/master'
SUPERFECTA_SOURCES_PATH='/var/www/html/admin/modules/superfecta/sources'
ASTERISK_AGIBIN_PATH='/var/lib/asterisk/agi-bin'
PYTHON_VERSION='3.6.0'
PYTHON_DOWNLOAD_URL="http://python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz"


################################################################################################
## INIT
################################################################################################
cd ~
if [ "$EUID" -ne 0 ]
then
	printf "\033[0;31mThis must be run as root or with sudo.\033[0m\n"
    exit
fi
printf "\033[0;33mAre you sure you want to install CallerLookup? [y/N] \033[0m\n"
read -r response
case "$response" in
    [yY][eE][sS]|[yY])
        ;;
    *)
        exit
        ;;
esac
mkdir /var/lib/CallerLookup
cd ~


################################################################################################
## DOWNLOAD SCRIPT FILES
################################################################################################
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


################################################################################################
## CREATE SETTINGS INI FILE ####################################################################
################################################################################################
printf "\033[0;33mDo you want to save your Google Acount Credentials in the config file? [y/N] \033[0m\n"
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
    *)
        ;;
esac

################################################################################################
## INSTALL DEPENDENCIES FROM YUM
################################################################################################
printf "\033[0;33mDo you want to automatically download and install dependencies? [y/N] \033[0m\n"
read -r response
case "$response" in
    [yY][eE][sS]|[yY])
        cd ~
        yum update -y
        command -v python >/dev/null 2>&1 || {
            printf "\033[0;32mPython...\033[0m\n"
            wget "${PYTHON_DOWNLOAD_URL}"
            tar xf "Python-${PYTHON_VERSION}.tar.xz"
            cd "Python-${PYTHON_VERSION}"
            eval Python-${PYTHON_VERSION}/configure --enable-optimizations
            make && make altinstall
        }
        cd ~
        #printf "\033[0;32mPython PIP...\033[0m\n"
        #wget get-pip.py https://bootstrap.pypa.io/get-pip.py
        #chmod +x get-pip.py
        #./get-pip.py
        ;;
    *)
        ;;
esac

install_pip_package() {
    printf "\033[0;32mInstalling $1...\033[0m\n"
    eval /usr/bin/pip3 install $1
}

printf "\033[0;33mDo you want to install Python3 packages from PIP3? [y/N] \033[0m\n"
read -r response
case "$response" in
    [yY][eE][sS]|[yY])
        install_pip_package selenium
        install_pip_package phonenumbers
        install_pip_package pyotp
        install_pip_package pyst2
        install_pip_package configparser
        install_pip_package http
        install_pip_package cookiejar
        install_pip_package parse
        install_pip_package requests
        exit
        ;;
    *)
        exit
        ;;
esac

################################################################################################
## FINISHED
################################################################################################
printf "\033[0;32mInstallation Complete.\033[0m\n"
exit
################################################################################################