#!/bin/bash
#
# Author:       Scott Philip (sp@scottphilip.com)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
#               CallerLookup Copyright (C) 2017 SCOTT PHILIP
#               This program comes with ABSOLUTELY NO WARRANTY
#               This is free software, and you are welcome to redistribute it
#               under certain conditions
#               https://github.com/scottphilip/caller-lookup/blob/master/LICENSE.md

printf "\033[92mInstalling PhantomJS Dependencies ... \033[0m\n"
if [ -n "$(command -v yum)" ]
then
    yum update -y
    yum install -y fontconfig freetype freetype-devel fontconfig-devel libstdc++
    yum install -y wget
fi
if [ -n "$(command -v apt-get)" ]
then
    apt-get update -y
    apt-get install -y libfreetype6 libfreetype6-dev
    apt-get install -y libfontconfig1 libfontconfig1-dev
    apt-get install -y wget
fi

printf "\033[92mInstalling PhantomJS ... \033[0m\n"
cd /usr/local
npm install phantomjs-prebuilt
if [[ ! -e /usr/bin/phantomjs ]]
then
    ln -s /usr/local/node_modules/.bin/phantomjs /usr/bin/phantomjs
fi

exit 0
