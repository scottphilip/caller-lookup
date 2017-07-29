# Author:       Scott Philip (sp@scottphilip.com)
# Version:      1.2 (25 July 2017)
# Source:       https://github.com/scottphilip/caller-lookup/
# Licence:      GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
import sys
import pprint
import sqlite3
from dateutil.relativedelta import relativedelta
from os.path import join
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from CallerLookup.Strings import *
from CallerLookup.Utils.Logs import *
from CallerLookup.Configuration import CallerLookupConfiguration

HTML_ROW_BEGIN = "<tr>"
HTML_ROW_END = "</tr>"
HTML_CELL_HEADER = "<th align=""left"" valign=""top"">{0}</th>"
HTML_CELL = "<td align=""left"" valign=""top"">{0}</td>"


def send_report(**kwargs):
    with __CallerLookupReportManager(**kwargs) as report_manager:
        return report_manager.send_report()


def record(config, number, region, int_dial_code, result, time_taken):
    with __CallerLookupReportManager(config=config) as report_manager:
        return report_manager.record(number, region, int_dial_code, result, time_taken)


class __CallerLookupReportManager(object):
    config = None
    db_file_name = "CallerLookup.db"
    tables = {
        "log": ["log_id INTEGER PRIMARY KEY AUTOINCREMENT",
                "log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "account text NOT NULL",
                "number text NOT NULL",
                "region text NULL",
                "int_dial_code NOT NULL",
                "result text NOT NULL",
                "time_taken text NOT NULL"]
    }

    def __init__(self, **kwargs):
        self.config = kwargs.pop("config", CallerLookupConfiguration(**kwargs))
        self.connection = sqlite3.connect(join(self.config.data_dir, self.db_file_name))
        for table_name in self.tables:
            self.connection.execute("CREATE TABLE IF NOT EXISTS {0} ({1})"
                                    .format(table_name,
                                            ", ".join(self.tables[table_name])))
        self.connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def record(self, number, region, int_dial_code, result, time_taken):
        try:
            self.connection.execute("INSERT INTO log "
                                    "(account, number, region, int_dial_code, result, time_taken) "
                                    "values (?, ?, ?, ?, ?, ?)",
                                    (self.config.account,
                                     number, region,
                                     int_dial_code,
                                     json.dumps(result),
                                     time_taken))
            self.connection.commit()
            return True
        except Exception as ex:
            log_error(self.config, "REPORT_RECORD", str(ex))
            return False

    def send_report(self):
        if self.config.settings[CallerLookupConfigStrings.REPORT][CallerLookupConfigStrings.IS_REPORT_ENABLED] is False:
            return True
        if not self.is_send_now():
            return True
        start_utc = datetime.utcnow()
        try:
            last_utc = datetime.strptime(self.config.settings[CallerLookupConfigStrings.REPORT]
                                         [CallerLookupConfigStrings.LAST_UTC],
                                         CallerLookupKeys.DATETIME_FMT)
        except:
            last_utc = None
        report = self.build_report(start_utc, last_utc)
        if report is None:
            return True
        if self.email_report(report, last_utc, start_utc):
            next_utc = self.get_next_utc(start_utc)
            self.config.settings[CallerLookupConfigStrings.REPORT][CallerLookupConfigStrings.LAST_UTC] = \
                start_utc.strftime(CallerLookupKeys.DATETIME_FMT)
            self.config.settings[CallerLookupConfigStrings.REPORT][CallerLookupConfigStrings.NEXT_UTC] = \
                next_utc.strftime(CallerLookupKeys.DATETIME_FMT)
            self.config.save()
            log_debug(self.config, "REPORT_EMAIL_SENT")
            return True
        return False

    def build_report(self, start_utc, last_utc):
        self.connection.row_factory = sqlite3.Row
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM log WHERE log_timestamp BETWEEN ? AND ?",
                    (last_utc if last_utc is not None else datetime(2000, 1, 1), start_utc))
        rows = cur.fetchall()
        if len(rows) == 0:
            return None

        table_html = "<html><body>"
        table_html += "<table>"
        table_html += HTML_ROW_BEGIN
        table_html += HTML_CELL_HEADER.format("Date/Time")
        table_html += HTML_CELL_HEADER.format("Phone Number")
        table_html += HTML_CELL_HEADER.format("Result")
        table_html += HTML_CELL_HEADER.format("Name")
        table_html += HTML_CELL_HEADER.format("Time Taken")
        table_html += HTML_ROW_BEGIN

        for row in rows:
            response = json.loads(row["result"])
            table_html += HTML_ROW_BEGIN
            table_html += HTML_CELL.format(row["log_timestamp"])
            table_html += HTML_CELL.format(row["number"])
            table_html += HTML_CELL.format(response["RESULT"])
            table_html += HTML_CELL.format(response["NAME"] if "NAME" in response else "")
            table_html += HTML_CELL.format(row["time_taken"])
            table_html += HTML_ROW_END

        table_html += "</table></body></html>"

        return table_html

    def email_report(self, report, last_utc, start_utc):
        address_from = self.config.settings[CallerLookupConfigStrings.REPORT][CallerLookupConfigStrings.REPORT_EMAIL_FROM]
        address_to = self.config.settings[CallerLookupConfigStrings.REPORT][CallerLookupConfigStrings.REPORT_RECIPIENTS]
        server_name = self.config.settings[CallerLookupConfigStrings.GENERAL][CallerLookupConfigStrings.SMTP_SERVER]

        msg = MIMEText(report, "html")
        msg["From"] = address_from
        msg["To"] = address_to
        if last_utc is not None:
            msg["Subject"] = "Caller Lookup Report ({0} - {1})".format(last_utc.date(), start_utc.date())
        else:
            msg["Subject"] = "Caller Lookup Report"

        s = smtplib.SMTP(server_name)
        try:
            if sys.version_info[0] >= 3:
                response = s.send_message(msg)
            else:
                response = s.sendmail(address_from, address_to, msg.as_string())
        except Exception as ex:
            log_error(self.config, ["EMAIL_REPORT", {"Exception": str(ex)}])
            return False
        finally:
            s.quit()
        if response is not None and len(response) > 0:
            log_info(self.config, ["EMAIL_REPORT_WARNING", {"Response": str(response)}])
        return True

    def is_send_now(self):
        next_utc = self.config.settings[CallerLookupConfigStrings.REPORT][CallerLookupConfigStrings.NEXT_UTC]
        if next_utc is None:
            return True
        return datetime.strptime(next_utc, CallerLookupKeys.DATETIME_FMT) <= datetime.utcnow()

    def get_next_utc(self, utc):
        mode = self.config.settings[CallerLookupConfigStrings.REPORT][CallerLookupConfigStrings.SEND_MODE]
        if mode == CallerLookupReportMode.EVERY_DAY:
            return utc.date() + timedelta(days=1)
        if mode == CallerLookupReportMode.EVERY_WEEKDAY:
            return utc.date() + timedelta(days=((0 - utc.weekday()) + 7) % 7)
        if mode == CallerLookupReportMode.WEEKLY:
            return utc.date() + timedelta(days=7)
        if mode == CallerLookupReportMode.MONTHLY:
            return utc.date() + relativedelta(months=1)
        raise Exception("CALLERLOOKUPREPORTMODE_INVALID")
