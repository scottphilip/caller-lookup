# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (20 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)

from datetime import datetime


def record(number, region, int_dial_code, result, time_taken):
    pass


def __get_report_body(number, region, int_dial_code, result, time_taken):
    body_template = "<html><body><h3>{0}</h3><table>{1}</table></body></html>"
    row_template = "<tr><td><b>{0}</b></td><td>{1}</td></tr>"
    rows = row_template.format("DATETIME", datetime.utcnow().strftime("%c") + " (UTC)")
    if region is not None:
        rows += row_template.format("TRUNK_REGION", region)
    if int_dial_code is not None:
        rows += row_template.format("TRUNK_INT_DIAL_CODE", int_dial_code)
    for key in result:
        rows += row_template.format(key, result[key])
    rows += row_template.format("TIME_TAKEN", time_taken)
    return body_template.format(number, row_template)
