import syslog as syslog


# singleton like class
class Syslog:
    __instance = None

    ''' redefined syslog constant in order to avoid any confusion between real syslog
    and our Sysog wrapper '''
    LOG_DEBUG = syslog.LOG_DEBUG
    LOG_INFO = syslog.LOG_INFO
    LOG_NOTICE = syslog.LOG_NOTICE
    LOG_WARNING = syslog.LOG_WARNING
    LOG_ALERT = syslog.LOG_ALERT

    @staticmethod
    def getInstance():
        if Syslog.__instance == None:
            Syslog()
        return Syslog.__instance

    def set_verbosity_policy(self, log_level):
        self.log_level = log_level

    def __init__(self):
      """ Virtually private constructor. """
      if Syslog.__instance != None:
          raise Exception("This is a private constructor, you shouldn't call it directly")
      else:
          self.log_level = syslog.LOG_INFO  # default log level is INFO
          syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
          Syslog.__instance = self

    ''' This function wraps the real syslog function in order to run it or not
    following the state of self.log_level '''
    def log(self, log_level, message):
        if log_level <= self.log_level:
            syslog.syslog(log_level, message)
