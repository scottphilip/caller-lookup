# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from appdirs import AppDirs
from CallerLookup.Strings import CallerLookupKeys
from cryptography.fernet import Fernet, InvalidToken
from base64 import b64encode, b64decode, urlsafe_b64encode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import sys
from os.path import isdir, join, isfile
from os import name as osname, makedirs
import hashlib
import socket


INVALID_DECRYPTION_KEY = "INVALID_DECRYPTION_KEY"
PRIVATE_KEY_DIR_NAME = ".keys"


def __get_system_key(account):
    try:
        machine_id = socket.gethostname()
    except:
        machine_id = account
    if sys.version_info[0] >= 3:
        machine_id = bytes(machine_id, encoding=CallerLookupKeys.UTF8)
    else:
        machine_id = bytes(machine_id)
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(machine_id)
    return urlsafe_b64encode(digest.finalize())


def __get_key(account):
    key_dir = join(AppDirs().site_data_dir, PRIVATE_KEY_DIR_NAME)
    h = hashlib.new("ripemd160")
    if sys.version_info[0] >= 3:
        account = bytes(account, CallerLookupKeys.UTF8)
    else:
        account = bytes(account)
    h.update(account)
    key_path = join(key_dir, ".{0}".format(h.hexdigest()))
    f = Fernet(key=__get_system_key(account))
    if not isfile(key_path):
        if not isdir(key_dir):
            makedirs(key_dir)
        key = Fernet.generate_key()
        with open(key_path, "w+") as file:
            encoded = b64encode(key)
            file.write(f.encrypt(encoded).decode(CallerLookupKeys.UTF8))
        if osname == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(key_path, 0x02)
            except:
                ignore = True
    with open(key_path, "r+") as file:
        if sys.version_info[0] >= 3:
            data = bytes(file.read(), encoding=CallerLookupKeys.UTF8)
        else:
            data = bytes(file.read())
        try:
            decrypted = f.decrypt(data)
            return b64decode(decrypted)
        except InvalidToken as inner_ex:
            raise Exception(INVALID_DECRYPTION_KEY, inner_ex)


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
