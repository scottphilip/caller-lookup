import os
import sys
import json
from datetime import datetime
from appdirs import AppDirs
from logging import getLogger, ERROR as LOG_ERROR, StreamHandler, Formatter, basicConfig
from CallerLookup.Strings import CallerLookupKeys
from CallerLookup.Configuration import CallerLookupConfiguration

NUMBER = "NUMBER"
REGION = "REGION"
REGION_DIAL_CODE = "REGION_DIAL_CODE"
EXPECTED = "EXPECTED"
NAME = "NAME"
SUCCESS = "SUCCESS"
UNKNOWN = "UNKNOWN"
INVALID_NUMBER = "INVALID_NUMBER"
ERROR = "ERROR"
MESSAGE = "MESSAGE"
USERNAME = "USERNAME"
RESULT = "RESULT"
PARAMETERS = "PARAMETERS"

TEST_DATA = [
    {
        PARAMETERS: {
            NUMBER: "2024561111",
            REGION: "US",
            REGION_DIAL_CODE: None
        },
        EXPECTED: {
            RESULT: SUCCESS,
            NAME: "White House"
        }
    },
    {
        PARAMETERS: {
            NUMBER: "+7 495 697-03-49",
            REGION: None,
            REGION_DIAL_CODE: None
        },
        EXPECTED: {
            RESULT: SUCCESS,
            NAME: "Kremlin"
        }
    },
    {
        PARAMETERS: {
            NUMBER: "(512) 555-6677",
            REGION: "US",
            REGION_DIAL_CODE: None
        },
        EXPECTED: {
            RESULT: UNKNOWN,
        }
    },
    {
        PARAMETERS: {
            NUMBER: "12345",
            REGION: None,
            REGION_DIAL_CODE: None
        },
        EXPECTED: {
            RESULT: INVALID_NUMBER,
        }
    },
]
FILENAME_TESTVARS = "TestVariables.json"


def get_config():
    is_debug = False
    if "IS_DEBUG" in os.environ:
        is_debug = bool(str(os.environ["IS_DEBUG"]))
    test_data = __get_test_var_data()
    account_email = test_data["username"]
    root_dir_path = os.path.join(AppDirs().user_data_dir,
                                 "CallerLookup",
                                 "TestData",
                                 str(datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S-%f")))[:-5]
    print("TEST_ROOT_DIR=" + root_dir_path)
    config_dir = os.path.join(root_dir_path, "Config")
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
    data_dir = os.path.join(root_dir_path, "Data")
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    log_dir = os.path.join(root_dir_path, "Log")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    cookies_path = os.path.join(data_dir,
                                "{0}.{1}".format(account_email.upper(),
                                                 CallerLookupKeys.COOKIE_FILE_EXT))
    config_path = os.path.join(config_dir,
                               "{0}.ini".format(CallerLookupKeys.APP_NAME))
    with open(config_path, "w") as file:
        file.write(str(test_data["config"]))
    print("CONFIG=" + str(test_data["config"]))
    with open(cookies_path, "w") as file:
        file.write(json.dumps(test_data["cookies"]))
    print("COOKIES=({0})".format(", ".join(test_data["cookies"])))
    config = CallerLookupConfiguration(account_email=account_email,
                                       config_dir=config_dir,
                                       data_dir=data_dir,
                                       log_dir=log_dir,
                                       logger=__get_logger(),
                                       is_debug=is_debug)
    config.test_root_folder = root_dir_path
    return config


def __get_logger(is_console=False):
    basicConfig(level=LOG_ERROR)
    logger = getLogger(CallerLookupKeys.APP_NAME)
    logger.setLevel(LOG_ERROR)
    if is_console:
        stream_handler = StreamHandler()
        stream_handler.setFormatter(Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"))
        logger.addHandler(stream_handler)


def __get_test_var_data():
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    test_var_json_path = os.path.join(root_path, FILENAME_TESTVARS)
    if not os.path.isfile(test_var_json_path):
        raise Exception("TEST_VAR_JSON_MISSING", test_var_json_path)
    with open(test_var_json_path) as file:
        return json.load(file)
