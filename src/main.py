import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess
from Events.DpkgEvents import DpkgEvents
from Events.FileEvents import FileEvents

import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

Notify.init("SCAP Watcher")

def handler(args):
    print("handler")
    Notify.Notification.new("Modification happens in package list !").show()
    
def handler_dump(event):
    Notify.Notification.new("File {0} modified !".format(event.src_path)).show()
    pass
    
fileEvents = FileEvents(debug=True)
fileEvents.add_file_listener(handler_dump, "/home/dom/test/", "*.txt")
fileEvents.add_file_listener(handler_dump, "/home/dom/test/", "test.xml")
fileEvents.start()

dpkgEvents = DpkgEvents()
dpkgEvents.add_listener(handler)
dpkgEvents.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
