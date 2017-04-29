#!/usr/bin/env python

# Usage:
#
#       exten => 12345,1,AGI(CallerLookup-SetCIDName.py)
#
# Author:       Scott Philip (sp@scottphilip.com)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
#               CallerLookup Copyright (C) 2017 SCOTT PHILIP
#               This program comes with ABSOLUTELY NO WARRANTY
#               This is free software, and you are welcome to redistribute it
#               under certain conditions
#               https://github.com/scottphilip/caller-lookup/blob/master/LICENSE.md

if __name__ == '__main__':

    import importlib.util
    spec = importlib.util.spec_from_file_location("CallerLookup", "/var/lib/CallerLookup/CallerLookup.py")
    CallerLookup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(CallerLookup)

    import sys
    import asterisk

    try:

        agi = asterisk.agi()

        caller_id = agi.env["agi_callerid"] if "agi_callerid" in agi.env else None
        if caller_id is None:
            exit(0)

        default_region = agi.env["agi_arg_1"] if "agi_arg_1" in agi.env else None

        caller_lookup = CallerLookup()
        result = caller_lookup.search(caller_id, default_region)

        agi.verbose("Python AGI Started")
        result = caller_lookup.search(caller_id)

        if result is None or result["result"] != "success":
            exit(0)

        agi.env["agi_calleridname"] = result["name"]

        exit(0)

    except Exception as e:

        sys.stderr.write("Caught Exception {}".format(str(e)))
        exit(1)
