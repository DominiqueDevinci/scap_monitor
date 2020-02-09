import time
import openscap_api as oscap
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess
from Events.DpkgEvents import DpkgEvents
from Events.FileEvents import FileEvents
from RuleParser.BindXCCDF import bind_xccdf_profile


import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

Notify.init("SCAP Watcher")

def handler(args):
    print("handler")
    Notify.Notification.new("Modification happens in package list !").show()
    

def handler_xccdf(rule, rs):
    if rs == oscap.xccdf.XCCDF_RESULT_PASS:
        Notify.Notification.new("Rule {0} have been triggered but is PASSED.".format(rule)).show()
    elif rs == oscap.xccdf.XCCDF_RESULT_FAIL:
        Notify.Notification.new("!!! Rule {0} have been triggered and is FAILED.".format(rule)).show()
    else:
        Notify.Notification.new("! Rule {0} have been triggered and cannot be evaluated !".format(rule)).show()
    
dpkgEvents = DpkgEvents()
dpkgEvents.add_listener(handler)
dpkgEvents.start()

bind_xccdf_profile('/home/dom/content/build/ssg-ubuntu1804-xccdf.xml',
            'anssi_np_nt28_restrictive', handler_xccdf, '/home/dom/content/build/ssg-ubuntu1804-cpe-dictionary.xml')

Notify.Notification.new("Listening events related to Scap Security Guide ... ").show()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
