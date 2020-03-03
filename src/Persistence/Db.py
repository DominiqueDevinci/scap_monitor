import sqlite3
from Dispatcher.Syslog import Syslog

syslog = Syslog.getInstance()

# singleton like class
class Db:
    __instance = None

    @staticmethod
    def getInstance():
        if Db.__instance == None:
            Db()
        return Db.__instance

    def __init__(self):
      """ Virtually private constructor. """
      if Db.__instance != None:
          raise Exception("This is a private constructor, you shouldn't call it directly")
      else:
          self.con = sqlite3.connect('scap_monitor.db')
          self.init_db()  # verify db and init it if needed
          Db.__instance = self

    def init_db(self):
        c = self.con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS rule_results(id INTEGER PRIMARY KEY, rule_name TEXT, rule_result SMALLINT, rule_date DATETIME);")
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
