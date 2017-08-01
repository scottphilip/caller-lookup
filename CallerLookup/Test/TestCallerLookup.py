import unittest
from time import sleep

import os.path

from CallerLookup.Test.Helper import *
from CallerLookup.Main import lookup_number


class TestMain(unittest.TestCase):

    config = None

    @classmethod
    def setUpClass(cls):
        cls.config = get_config()

    @classmethod
    def tearDownClass(cls):
        close_logger(cls.config.logger)

    def validate_result(self, expected, actual):
        for key in expected[EXPECTED]:
            self.assertTrue(key in actual, "{0} NOT IN {1}".format(key, str(actual)))
            self.assertEqual(expected[EXPECTED][key],
                             actual[key],
                             "{0} Key Not as expected.  Found {1}.  Expected {2}.  {3}"
                             .format(key, actual[key], expected[EXPECTED][key], str(actual)))

    def test_main_lookup_number_0_success(self):
        try:

            data = TEST_DATA[0]
            result = lookup_number(number=data[PARAMETERS][NUMBER],
                                   region=data[PARAMETERS][REGION],
                                   region_dial_code=data[PARAMETERS][REGION_DIAL_CODE],
                                   config=self.config)
            self.validate_result(data, result)

        except:

            raise

    # def test_main_lookup_number_1_success(self):
    #     data = TEST_DATA[1]
    #     result = lookup_number(number=data[PARAMETERS][NUMBER],
    #                            region=data[PARAMETERS][REGION],
    #                            region_dial_code=data[PARAMETERS][REGION_DIAL_CODE],
    #                            config=self.config)
    #     self.validate_result(data, result)
    #
    # def test_main_lookup_number_2_unknown(self):
    #     data = TEST_DATA[2]
    #     result = lookup_number(number=data[PARAMETERS][NUMBER],
    #                            region=data[PARAMETERS][REGION],
    #                            region_dial_code=data[PARAMETERS][REGION_DIAL_CODE],
    #                            config=self.config)
    #     self.validate_result(data, result)
    #
    # def test_main_lookup_number_3_invalid(self):
    #     data = TEST_DATA[3]
    #     result = lookup_number(number=data[PARAMETERS][NUMBER],
    #                            region=data[PARAMETERS][REGION],
    #                            region_dial_code=data[PARAMETERS][REGION_DIAL_CODE],
    #                            config=self.config)
    #     self.validate_result(data, result)

if __name__ == '__main__':
    unittest.main()

