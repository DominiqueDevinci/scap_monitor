import time
import openscap_api as oscap
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess
from Events.DpkgEvents import DpkgEvents
from Events.FileEvents import FileEvents
from RuleParser.BindXCCDF import bind_xccdf_profile
from Dispatcher.Syslog import Syslog
import syslog as syslog

sysl = Syslog.getInstance()

import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

Notify.init("SCAP Watcher")

def handler(args):
    print("handler")
    Notify.Notification.new("Modification happens in package list !").show()


security_event_notif = Notify.Notification.new(
    'SCAP Monitor: new security events !',
    "",
    "dialog-danger"
)
security_event_notif.set_timeout(3000)
se_notif_body='' # cache for notification body

def handler_xccdf(rule, rs):
    global se_notif_body, security_event_notif, syslog

    if rs == oscap.xccdf.XCCDF_RESULT_PASS:
        sysl.syslog(syslog.LOG_INFO, "Rule {0} is evaluated as PASSED.".format(rule))
        se_notif_body+="\n{0}: <i>PASSED</i>.".format(rule)
    elif rs == oscap.xccdf.XCCDF_RESULT_FAIL:
        sysl.syslog(syslog.LOG_ALERT, "Rule {0} is evaluated as FAILED !".format(rule))
        se_notif_body+="\n{0}: <b>FAILED</b>.".format(rule);
    else:
        sysl.syslog(syslog.LOG_WARNING, "Rule {0} is evaluated as FAILED !".format(rule))
        se_notif_body+="\n{0}: cannot be evaluated.".format(rule);

    security_event_notif.update(
        'SCAP Monitor: new security events !',
        se_notif_body,
        "dialog-warning"
    )
    security_event_notif.show()

bind_xccdf_profile('/home/dom/content/build/ssg-ubuntu1804-xccdf.xml',
            'anssi_np_nt28_restrictive', handler_xccdf, '/home/dom/content/build/ssg-ubuntu1804-cpe-dictionary.xml')


dpkgEvents = DpkgEvents()
dpkgEvents.add_listener(handler)
dpkgEvents.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
