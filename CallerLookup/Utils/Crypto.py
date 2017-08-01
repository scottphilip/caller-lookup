# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
from CallerLookup.Strings import CallerLookupKeys
from CallerLookup.Utils.Logs import *
from cryptography.fernet import Fernet, InvalidToken
from base64 import b64encode, b64decode, urlsafe_b64encode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import sys
from os.path import isdir, join, isfile
from os import name as osname, makedirs
import hashlib
import re
import platform


INVALID_KEY = "INVALID_KEY"
PRIVATE_KEY_DIR_NAME = ".keys"


def __get_system_key(account):
    try:
        key = ""
        for item_name in platform.uname():
            key += platform.uname()[item_name]
        key = re.sub("[a-zA-Z0-9]", "", key.upper())
    except:
        key = re.sub("[a-zA-Z0-9]", "", account.upper())

    if sys.version_info[0] >= 3:
        key_bytes = bytes(key, encoding=CallerLookupKeys.UTF8)
    else:
        key_bytes = bytes(key)
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(key_bytes)
    return urlsafe_b64encode(digest.finalize()), key


def __get_key(config, account=None):
    key_dir = join(config.data_dir, PRIVATE_KEY_DIR_NAME)
    if not isdir(key_dir):
        makedirs(key_dir)
    h = hashlib.new("ripemd160")
    selected_account = account.upper() if account is not None else config.account.upper()
    if sys.version_info[0] >= 3:
        account_bytes = bytes(selected_account, CallerLookupKeys.UTF8)
    else:
        account_bytes = bytes(selected_account)
    h.update(account_bytes)
    key_path = join(key_dir, ".{0}".format(h.hexdigest()))
    system_key, system_key_str = __get_system_key(selected_account)
    log_debug(config, "SYSTEM_KEY", system_key_str, system_key)
    f = Fernet(key=system_key)
    if not isfile(key_path):
        if not isdir(key_dir):
            makedirs(key_dir)
        key = Fernet.generate_key()
        with open(key_path, "w") as file:
            encoded = b64encode(key)
            file.write(f.encrypt(encoded).decode(CallerLookupKeys.UTF8))
        log_debug(config, "CRYPTO_KEY_CREATED", selected_account, key_path)
        if osname == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(key_path, 0x02)
            except:
                ignore = True
    with open(key_path, "r") as file:
        if sys.version_info[0] >= 3:
            data = bytes(file.read(), encoding=CallerLookupKeys.UTF8)
        else:
            data = bytes(file.read())
    try:
        decrypted = f.decrypt(data)
        return b64decode(decrypted)
    except InvalidToken as inner_ex:
        raise Exception(INVALID_KEY, inner_ex.args,
                        {
                            "ACCOUNT": selected_account,
                            "KEY_PATH": key_path,
                            "SYSTEM_KEY": (system_key_str, system_key)
                        })


def encrypt(config, plain_text, account=None):
    try:
        if not plain_text:
            return ""
        from cryptography.fernet import Fernet
        if sys.version_info[0] >= 3:
            bytes_text = bytes(plain_text, encoding="utf-8")
        else:
            bytes_text = bytes(plain_text)
        cipher_suite = Fernet(key=__get_key(config, account))
        token = cipher_suite.encrypt(bytes_text)
        return b64encode(token).decode(CallerLookupKeys.UTF8)
    except Exception as ex:
        log_error(config, "ENCRYPTION_ERROR", ex.args, ex)
        return "ERROR {0}".format(str(ex.args))


def decrypt(config, encrypted_text, account=None):
    try:
        if not encrypted_text:
            return ""
        if sys.version_info[0] >= 3:
            data = b64decode(bytes(encrypted_text, encoding=CallerLookupKeys.UTF8))
        else:
            data = b64decode(bytes(encrypted_text))
        cipher_suite = Fernet(key=__get_key(config, account))
        return cipher_suite.decrypt(data).decode(CallerLookupKeys.UTF8)
    except Exception as ex:
        if config is None:
            raise
        log_error(config, "DECRYPTION_ERROR", ex.args, ex)
        return ""
