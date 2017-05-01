#!/bin/bash
# Author:       Scott Philip (sp@scottphilip.com)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
#               CallerLookup Copyright (C) 2017 SCOTT PHILIP
#               This program comes with ABSOLUTELY NO WARRANTY
#               This is free software, and you are welcome to redistribute it
#               under certain conditions
#               https://github.com/scottphilip/caller-lookup/blob/master/LICENSE.md

printf "\033[0;32mInstalling Python 3.6.1 Dependencies...\032[0m\n"

if [ -n "$(command -v yum)" ]
then
    yum update
    yum groupinstall -y "development tools"
    yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel
    yum install -y wget
fi
if [ -n "$(command -v apt-get)" ]
then
    apt-get update -y
    apt-get install -y build-essential checkinstall
    apt-get install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
    apt-get install -y wget
fi

cd ~
printf "\033[0;Downloading Python 3.6.1...\032[0m\n"
wget http://python.org/ftp/python/3.6.1/Python-3.6.1.tar.xz
wget https://bootstrap.pypa.io/get-pip.py
tar xf Python-3.6.1.tar.xz
cd Python-3.6.1
printf "\033[0;Installing Python 3.6.1...\032[0m\n"
./configure --prefix=/usr --enable-shared LDFLAGS="-Wl,-rpath /usr/lib"
./make
./make altinstall

cd ~
python3.6.1 get-pip.py
