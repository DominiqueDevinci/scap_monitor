'''
This is a singleton like class, but an SQLite object can only
be used in the same thread so it must manage to create on object per thread id
'''

import sqlite3
import threading
from Dispatcher.Syslog import Syslog

syslog = Syslog.getInstance()

# singleton like class
class Db:
    __instance = {}

    @staticmethod
    def getInstance():
        tid=threading.get_ident()
        if Db.__instance.get(tid) == None:
            Db(tid)
        return Db.__instance.get(tid)

    def __init__(self, tid = None):
      syslog.log(Syslog.LOG_DEBUG, "db created in thread {0}".format(threading.get_ident()))
      
      """ Virtually private constructor. """
      if tid is None or Db.__instance.get(tid) is not None:
          raise Exception("This is a private constructor, you shouldn't call it directly")
      else:
          self.con = sqlite3.connect('scap_monitor.db')
          self.init_db()  # verify db and init it if needed
          Db.__instance[tid] = self

    def init_db(self):
        c = self.con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS rule_results(id INTEGER PRIMARY KEY, \
            rule_name TEXT, rule_result SMALLINT, trigger SMALLINT, rule_date DATETIME);")
        # trigger field: 0 => initial_scan, 1 => triggered by monitor '''

        self.con.commit()

    def is_results_empty(self):
        c = self.con.cursor()
        nb = c.execute('SELECT COUNT(*) FROM rule_results').fetchone()[0]
        return nb == 0

    def get_cursor(self):
        return self.con.cursor()

    def commit(self):
        self.con.commit()

    def __del__(self):
        self.con.close()
