import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess
from gi.repository import Notify
from threading import Timer


'''
FIXME: This class is not really proper even it's works.*
For instance, with an update which take time, the listeners are triggered 2x.
'''

class DpkgEvents:
    def __init__(self):
        '''
        For now we don't distinguish between install / remove / update / upgrade
        but later we will perhaps be more accurate, so we keep the possibility to 
        have different types of listeners (by default it's "any" at the moment).
        '''
        self.listeners = {"any": []}
        
        '''
        The file /var/lib/dpkg/lock is modified 2x on an installation (begin and end)
        or 3x when removing packages (2x at the begin, 1 at the end). 
        For the moment i only use a delay, it's not really "proper" but it's safer
        (since it can be even or impar, it's difficult to deal with a counter)
        
        Furthermore, the goal of this software isn't to fastly proactive,
        only to stay compliant (no need to run the scan 1 sec after an event)
        '''
        self.delaying = False
        
        self.pause = False
        self.pause_ignoring = False #  ingore event which happens during a pause
        
        self.event_handler = PatternMatchingEventHandler(["/var/lib/dpkg/lock"],
            [], False, True)
            
        self.event_handler.on_modified = self._on_modified
        self.observer = Observer()
        self.observer.schedule(self.event_handler, "/var/lib/dpkg", recursive=False)
        
    def _on_modified(self, event):
        print("modified ...")
        if not self.delaying:
            self.delaying = True
            t = Timer(10, self._trigger_listeners, [["any"]])
            t.start()
    
    def _trigger_listeners(self, categories=["any"]):
        if not self.pause:
            for c in categories:
                for l in self.listeners[c]:
                    l({})  # empty argument list (nothing usefull to know for the moment)
        self.delaying = False

    def start(self):
        self.observer.start()
        
    def pause(self, ignoring=False):
        self.pause = True
        self.pause_ignoring = ignoring
        
    def resume(self):
        self.pause = False
        # TODO : handle the case pause_ignoring

    def add_listener(self, listener, cat="any"):
        self.listeners[cat].append(listener)
        
    def remove_listener(self, listener):
        self.remove(listener)

