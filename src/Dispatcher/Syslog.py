import syslog as syslog


# singleton like class
class Syslog:

   __instance = None
   @staticmethod
   def getInstance():
      if Syslog.__instance == None:
         Syslog()
      return Syslog.__instance

   def __init__(self):
      """ Virtually private constructor. """
      if Syslog.__instance != None:
          raise Exception("This is a private constructor, you shouldn't call it directly")
      else:
          syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
          syslog.syslog(syslog.LOG_INFO, 'SCAP Monitor daemon is listening ... ')
          Syslog.__instance = syslog
