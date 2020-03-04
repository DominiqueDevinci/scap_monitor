import time
import openscap_api as oscap
import subprocess
import argparse

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from Events.DpkgEvents import DpkgEvents
from Events.FileEvents import FileEvents
from RuleParser.BindXCCDF import bind_xccdf_profile
from Dispatcher.Syslog import Syslog
from Dispatcher.DesktopNotif import DesktopNotif
from Persistence.Db import Db
from utils import initial_scan, load_xccdf_session, get_previous_rule_results, \
                  result2str

syslog = Syslog.getInstance()
desktop = DesktopNotif.getInstance()
desktop.set_timeout(10000)  # 10 sec timeout for notifs

#time.sleep(20)

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ALERT'],
        help="Verbosity level, corresponding to syslog priority.", default="INFO")

parser.add_argument("-n", "--desktop-notify", action="store_true",
                    help="Show desktop notifs with noticeable events .")

parser.add_argument("--dpkg", action="store_true",
                    help="Show desktop notifs with noticeable events .")

parser.add_argument("-c", "--change-only", action="store_true",
                    help="Notify only when a rule result changes.")

args = parser.parse_args()


''' Manage verbosity '''
if args.verbosity == "DEBUG":
    syslog.set_verbosity_policy(syslog.LOG_DEBUG)
elif args.verbosity == "WARGNING":
    syslog.set_verbosity_policy(syslog.LOG_WARNING)
elif args.verbosity == "ALERT":
    syslog.set_verbosity_policy(syslog.LOG_ALERT)

desktop.set_display_policy(args.desktop_notify)

syslog.log(syslog.LOG_INFO, "SCAP monitor is starting, verbosity = {0}".format(args.verbosity))


'''
     ********       EVENT HANDLERS           ********
'''

def handler_dpkg(args):
    print("handler")

def handler_xccdf(rule, rs):
    _db = Db.getInstance()

    prev_rs = get_previous_rule_results(rule, _db)
    syslog.log(Syslog.LOG_DEBUG, "previous/new result for {0} is {1}/{2}"
               .format(rule, result2str(prev_rs), result2str(rs)))

    _db.get_cursor().execute("INSERT INTO rule_results(rule_name, rule_result, trigger, rule_date) \
    VALUES('{0}', '{1}', 0, datetime('now'));".format(rule, rs))
    _db.commit()

    if not args.change_only or prev_rs != rs:
        if rs == oscap.xccdf.XCCDF_RESULT_PASS:
            syslog.log(syslog.LOG_INFO, "{0}: {1} => <i>PASS</i>".format(rule, result2str(prev_rs)))
            desktop.send_message("{0}: {1} => <i>PASS</i>".format(rule, result2str(prev_rs)))
        elif rs == oscap.xccdf.XCCDF_RESULT_FAIL:
            syslog.log(syslog.LOG_ALERT, "{0}: {1} => <b>FAIL</b>".format(rule, result2str(prev_rs)))
            desktop.send_message("{0}: {1} => <b>FAIL</b>".format(rule, result2str(prev_rs)))
        else:
            syslog.log(syslog.LOG_WARNING, "Rule {0} cannot be evaluated.".format(rule))
            desktop.send_message("{0}: <b>cannot be evaluated</b>.".format(rule))


'''
    Load xccdf session
'''

xccdf_session = load_xccdf_session('/home/dom/content/build/ssg-ubuntu1804-xccdf.xml',
            'anssi_np_nt28_restrictive', '/home/dom/content/build/ssg-ubuntu1804-cpe-dictionary.xml')

initial_scan(xccdf_session)

'''
     ********       BINDING WITH EVENT WATCHERS          ********
'''

# Bind to an XCCDF Benchmark
bind_xccdf_profile(xccdf_session, '/home/dom/content/build/ssg-ubuntu1804-xccdf.xml',
                   'anssi_np_nt28_restrictive', handler_xccdf)

# Listen for dpkg events.
if args.dpkg is True:
    dpkgEvents = DpkgEvents()
    dpkgEvents.add_listener(handler)
    dpkgEvents.start()


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
