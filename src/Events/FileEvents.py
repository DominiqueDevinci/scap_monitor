import time, os, re
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess
from gi.repository import Notify
from threading import Timer
from pprint import pprint
import sys


''' the design of this program plan to be able to process a watchdog_pattern
     in order to convert it in a proper regex, but for now compile it is sufficient '''
     
def compile_watchdog_pattern(orig_pattern, debug=False):
    pattern=orig_pattern.replace('/', '\/')
    pattern=pattern.replace('.', '\.')
    pattern=pattern.replace('*', '(.+)')
    
    if debug:
        print("Convert from watchdog pattern {0} to regex : {1}".format(orig_pattern, pattern))
    
    return re.compile(pattern)


class FilePattern(object):
    '''
    This class is used for convenience, and should contains these attributes:
        - watchdog_pattern (like /home/foo/*.txt )
        - regex  (contains the equivalent pre-compiled regex, here /home/foo/(
    '''
    def __eq__(self, other):
        return self.watchdog_pattern == other.watchdog_pattern

    def __hash__(self):
        return self.watchdog_pattern.__hash__()

    pass

class FileEvents:
    def __init__(self, debug=False):
        self.debug=debug
        self.listeners = dict()
        self.observers = dict()  # one observer/handler by directory

        '''
        The listeners are classified by directories and then files, ex:
        {"/home/foo/" => {"bar.txt"=>callback}} listen for /home/foo/bar.txt
        and
        {{"/home/foo/" => {"*.txt"=>callback}} listen for all txt files
        
        For now listen for a directort isn't supported, because we don't need it yet.
        
        This structure aim to minimize the number of observers.
        '''
    
    def _map_watchdog_pattern(pattern):
        return pattern.watchdog_pattern
        
    def _map_regex(pattern):
        return pattern.watchdog_pattern 
        
    def _on_event(self, event):
        directory = os.path.dirname(event.src_path)
        for pattern in self.listeners[directory]:
            if pattern.regex.match(event.src_path):
                for callback in self.listeners[directory][pattern]:
                    callback(event)

    def start(self):
        for o in self.observers:
            o.start()
        
    def add_file_listener(self, filepath, callback):
        self.add_file_pattern_listener(os.path.dirname(filepath),
                    os.path.basename(filepath), callback)

    def add_file_pattern_listener(self, directory, file_pattern, callback):
        
        if directory.endswith('/'):
            directory=directory[:-1]
            
        if not os.path.isdir(directory):
            ''' FIXME '''
            sys.stderr.write("[warning] directory {0} doesn't exists and can't monitored\n"
                             .format(directory))
            return
            
        if directory not in self.listeners:
            self.listeners[directory]=dict()
            self.observers[directory]=None  # init the observer to null
        
        pattern=FilePattern()       
       
        pattern.regex=compile_watchdog_pattern(directory+'/'+file_pattern, self.debug)
        pattern.watchdog_pattern=directory+'/'+file_pattern
       
        if self.listeners[directory].get(pattern) is None:
            self.listeners[directory][pattern]=[callback]
        else:
            self.listeners[directory][pattern].append(callback)
            
    def start(self):
        nb_listeners = 0
        for directory, patterns in self.listeners.items():
            watchdog_patterns = list(map(lambda p: p.watchdog_pattern, patterns.keys()))
            nb_listeners += len(watchdog_patterns)
            
            print("listening on patterns {0}".format(watchdog_patterns))
            
            tmp_handler = PatternMatchingEventHandler(watchdog_patterns, [], False, True)
        
            
            tmp_handler.on_modified=self._on_event
            
            self.observers[directory]=Observer()
            self.observers[directory].schedule(tmp_handler, directory, recursive=False)
            self.observers[directory].start()
            
        print("[FileEvents] {0} observers launched monitoring {1} file patterns."
              .format(len(self.observers.keys()), nb_listeners))
              

