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

syslog = Syslog.getInstance()
desktop = DesktopNotif.getInstance()

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ALERT'],
        help="Verbosity level, corresponding to syslog priority.", default="INFO")

parser.add_argument("-n", "--desktop-notify", action="store_true",
                    help="Show desktop notifs with noticeable events .")

parser.add_argument("--dpkg", action="store_true",
                    help="Show desktop notifs with noticeable events .")

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
    if rs == oscap.xccdf.XCCDF_RESULT_PASS:
        syslog.log(syslog.LOG_INFO, "Rule {0} is evaluated as PASSED.".format(rule))
        desktop.send_message("{0}: <i>PASSED</i>.".format(rule))
    elif rs == oscap.xccdf.XCCDF_RESULT_FAIL:
        syslog.log(syslog.LOG_ALERT, "Rule {0} is evaluated as FAILED !".format(rule))
        desktop.send_message("{0}: <b>FAILED</b>.".format(rule))
    else:
        syslog.log(syslog.LOG_WARNING, "Rule {0} is evaluated as FAILED !".format(rule))
        desktop.send_message("{0}: cannot be evaluated.".format(rule))


'''
     ********       BINDING WITH EVENT WATCHERS          ********
'''

# Bind to an XCCDF Benchmark
bind_xccdf_profile('/home/dom/content/build/ssg-ubuntu1804-xccdf.xml',
            'anssi_np_nt28_restrictive', handler_xccdf, '/home/dom/content/build/ssg-ubuntu1804-cpe-dictionary.xml')

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
