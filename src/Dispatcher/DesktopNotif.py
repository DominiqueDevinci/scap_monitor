'''
This is an abstract class for desktop notifications.
For the moment only Gtk is supported.

The class use a signleton pattern to be unique (and conditonned with parameter
--desktop-notif).

The abstract methhods must be overriden by the children class, for instance GtkNotif
(which use libnotify python API).
'''


''' Manage import and available libraries '''
from Dispatcher.Syslog import Syslog
syslog = Syslog.getInstance()

libs = {'gtk_notify': False}  # availability of notif libraries.

try:
    import gi
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify
    syslog.log(syslog.LOG_DEBUG, "Gtk Libnotify 0.7 is available.")
    libs['gtk_notify'] = True
except ImportError:
    syslog.log(syslog.LOG_DEBUG, "Gtk Libnotify 0.7 is NOT available.")


''' Main singleton class '''
# singleton like class
class DesktopNotif:
    __instance = None
    __display = False # by default desktop notifs are disabled

    @staticmethod
    def getInstance():
        if DesktopNotif.__instance == None:
            DesktopNotif()
        return DesktopNotif.__instance

    ''' update static variable which define if we should display or not desktop notifs '''
    def set_display_policy(self, display):
        self.__display = display

    def __init__(self):
      """ Virtually private constructor. """
      if DesktopNotif.__instance != None:
          raise Exception("This is a private constructor, you shouldn't call it directly")
      else:
          Notify.init("SCAP Monitor")

          self.title = 'SCAP Monitor: security compliance events !'
          self.icon = 'dialog-danger'
          self.current_notif_body = ""

          self.current_notif = Notify.Notification.new(
              self.title,
              self.current_notif_body,
              self.icon
          )

          self.current_notif.set_timeout(5000)  # default timeout is 5sec

          DesktopNotif.__instance = self

    def set_title(self, title):
        self.title = title

    def set_timeout(self, timeout):
        self.timeout = timeout

    # example : dialog-danger
    def set_icon(self, icon):
        self.icon = icon

    def send_message(self, message):
            self.current_notif_body += "\n" + message

            self.current_notif.update(
                self.title,
                self.current_notif_body,
                self.icon
            )
            self.current_notif.show()
