#!/usr/bin/env python
import sys


if __name__ == '__main__':

    import importlib.util
    spec = importlib.util.spec_from_file_location("CallerLookup", "/var/lib/CallerLookup/CallerLookup.py")
    CallerLookup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(CallerLookup)

    import sys
    import asterisk

    try:

        agi = asterisk.AGI()

        caller_id = agi.env["agi_callerid"] if "agi_callerid" in agi.env else None
        if caller_id is None:
            exit(0)

        default_region = agi.env["agi_arg_1"] if "agi_arg_1" in agi.env else None

        settings = {
            "settings_path": "/var/lib/CallerLookup/CallerLookup.ini"
        }

        caller_lookup = CallerLookup(settings)
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
