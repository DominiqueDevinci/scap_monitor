import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess
from gi.repository import Notify
from DpkgEvents import DpkgEvents

Notify.init("SCAP Watcher")

def handler(args):
    print("handler")
    Notify.Notification.new("Modification happens in package list !").show()


dpkgEvents = DpkgEvents()
dpkgEvents.add_listener(handler)
dpkgEvents.start()

try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
