# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.1 (20 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from CallerLookup.Configuration import *
from CallerLookup.Strings import CallerLookupKeys
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode, urlsafe_b64encode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import ctypes
import sys
from os.path import isdir
from os import name as osname
import hashlib


def __get_system_key(account):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(account)
    return urlsafe_b64encode(digest.finalize())


def __get_key(account):
    key_dir = join(AppDirs().site_data_dir, ".tokens")
    h = hashlib.new("ripemd160")
    if sys.version_info[0] >= 3:
        account = bytes(account, CallerLookupKeys.UTF8)
    else:
        account = bytes(account)
    h.update(account)
    key_path = join(key_dir, "{0}.txt".format(h.hexdigest()))
    f = Fernet(key=__get_system_key(account))
    if not isfile(key_path):
        if not isdir(key_dir):
            makedirs(key_dir)
        key = Fernet.generate_key()
        with open(key_path, "w+") as file:
            encoded = b64encode(key)
            file.write(f.encrypt(encoded).decode(CallerLookupKeys.UTF8))
        if osname == 'nt':
            if not ctypes.windll.kernel32.SetFileAttributesW(key_path, 0x02) \
                    or not ctypes.windll.kernel32.SetFileAttributesW(key_dir, 0x02):
                raise ctypes.WinError()
    with open(key_path, "r+") as file:
        if sys.version_info[0] >= 3:
            data = bytes(file.read(), encoding=CallerLookupKeys.UTF8)
        else:
            data = bytes(file.read())
        return b64decode(f.decrypt(data))


def encrypt(account, plain_text):
    if not plain_text:
        return ""
    from cryptography.fernet import Fernet
    if sys.version_info[0] >= 3:
        bytes_text = bytes(plain_text, encoding="ascii")
    else:
        bytes_text = bytes(plain_text)
    cipher_suite = Fernet(key=__get_key(account))
    token = cipher_suite.encrypt(bytes_text)
    return b64encode(token).decode(CallerLookupKeys.UTF8)


def decrypt(account, encrypted_text):
    if not encrypted_text:
        return ""
    if sys.version_info[0] >= 3:
        data = b64decode(bytes(encrypted_text, encoding=CallerLookupKeys.UTF8))
    else:
        data = b64decode(bytes(encrypted_text))
    cipher_suite = Fernet(key=__get_key(account))
    return cipher_suite.decrypt(data).decode(CallerLookupKeys.UTF8)
