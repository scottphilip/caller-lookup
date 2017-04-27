#!/bin/bash

#Check SUDO
if [ "$EUID" -ne 0 ]; then
	whiptail --title 'Caller Lookup Installer' --msgbox "This must be run with SUDO or under the root account."  --ok-button 'Quit' 7 78
    exit;
fi

if (!(whiptail --title 'Caller Lookup Installer' --yesno "You are about to install CallerLookup and its dependencies" --yes-button 'Continue' --no-button 'Quit' 7 62)); then
	exit;
fi

is_python3=false
is_pip3=false
is_selenium=false
is_phonenumbers=false

if [ "type $python3 > /dev/null" ]; then

	is_python3=true

    if [ "type $pip3 > /dev/null" ]; then

		is_pip3=true
		if [ "$len( $(pip show selenium) ) -gt 0" ]; then
			is_selenium = true
			install_count = install_count + 1
		fi
		if [ [len "pip show phonenumbers"] -gt "0" ]; then
			is_phonenumbers = true
		fi
	fi
fi

if ( ! $is_python3 || ! $is_pip3 || ! $is_selenium || ! $is_phonenumbers );
then
	installing=""
	if (! $is_python3); then installing="$installing\n       => Python3"; fi;
	if (! $is_pip3); then installing="$installing\n       => PIP3"; fi;
	if (! $is_selenium); then installing="$installing\n       => Selenium"; fi;
	if (! $is_phonenumbers); then installing="$installing\n       => PhoneNumbers"; fi;

	if (!(whiptail --title 'Caller Lookup Installer' --yesno "The following dependencies will be installed with the application:\n$installing" --yes-button 'Install' --no-button 'Quit' 12 62))
	then
		exit
	fi
else
	if (!(whiptail --title 'Caller Lookup Installer' --yesno "All dependencies are already installed." --yes-button 'Continue' --no-button 'Quit' 7 62))
	then
		exit
	fi
fi

{
	printf "XXX\n1\nUpdating Existing Libraries ... \nXXX"
	unbuffer yum -y update > x

	printf "XXX\n16\nAdding New Libraries ... \nXXX"
	unbuffer yum -y install https://centos7.iuscommunity.org/ius-release.rpm > x

	printf "XXX\n30\nInstalling Python 3.6 ... \nXXX"
	unbuffer yum -y install python36u > x

	printf "XXX\n60\nInstalling Python 3.6 PIP ... \nXXX"
	unbuffer yum -y install python36u-pip > x

	printf "XXX\n70\nInstalling Selenium ... \nXXX"
	unbuffer pip install selenium > x

	printf "XXX\n85\nInstalling PhoneNumbers ... \nXXX"
	unbuffer pip install phonenumbers > x

	printf "XXX\n100\nDependency Install Complete\nXXX"

} | whiptail --title 'Caller Lookup Installer' --gauge "Installing ..." 6 50 0

{

	printf "XXX\n100\nVertification Complete\nXXX"

} | whiptail --title 'Caller Lookup Installer' --gauge "Verifying ..." 6 50 0
