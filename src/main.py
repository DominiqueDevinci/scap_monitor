import time
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
    
    
dpkgEvents = DpkgEvents()
dpkgEvents.add_listener(handler)
dpkgEvents.start()

bind_xccdf_profile('/home/dom/content/build/ssg-ubuntu1804-xccdf.xml',
            'anssi_np_nt28_restrictive', '/home/dom/content/build/ssg-ubuntu1804-cpe-dictionary.xml')

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
