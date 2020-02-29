'''
This is an abstract class for desktop notifications.
For the moment only Gtk is supported.

The class use a signleton pattern to be unique (and conditonned with parameter
--desktop-notif).

The abstract methhods must be overriden by the children class, for instance GtkNotif
(which use libnotify python API).
'''

import time, os

''' Manage import and available libraries '''
from Dispatcher.Syslog import Syslog
syslog = Syslog.getInstance()

libs = {'notify2': False}  # availability of notif libraries.

pixbuf_icon = None

try:
    import notify2

    syslog.log(syslog.LOG_INFO, "Gtk/Qt notify2 binding is available.")
    libs['notify2'] = True
except ImportError:
    syslog.log(syslog.LOG_INFO, "Gtk/Qt notify2 binding is NOT available.")

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
            notify2.init("SCAP Monitor")

            self.title = 'SCAP Monitor: security compliance events !'
            self.message_queue = list()
            self.current_notif_body = ""
            self.icon = os.path.dirname(__file__)+"/scap_monitor.ico"

            self.current_notif = notify2.Notification(
                self.title,
                self.current_notif_body,
                self.icon
            )

            self.timeout = 5000
            self.current_notif.set_timeout(5000)  # default timeout is 5ses

            DesktopNotif.__instance = self

    def set_title(self, title):
        self.title = title

    def set_timeout(self, timeout):
        self.timeout = timeout

    # example : dialog-danger
    def set_icon(self, icon):
        self.icon = icon

    def update_msg_queue(self):
        current_time = time.time()
        updated = False

        ''' curiously, not all messages are fetched using for msg in self.message_queue
        so i use indexes but in reverse order to be able to remove them without
        shifting other indexes. '''
        for i in range(len(self.message_queue)-1, -1, -1):
            msg = self.message_queue[i]
            if msg.expire < current_time:
                del self.message_queue[i]
                updated = True
                
        return updated

    def send_message(self, message):
        new_msg = DesktopMessage(message, self.timeout)
        self.message_queue.append(new_msg)
        if self.update_msg_queue():
            self.current_notif_body=""
            for msg in self.message_queue:
                self.current_notif_body  += "\n" + msg.message
        else:
            self.current_notif_body  += "\n" + new_msg.message

        self.current_notif.update(
            self.title,
            self.current_notif_body,
            self.icon
        )
        self.current_notif.show()

''' This class aims to destroy messages after a defined timeout
because messages are all displayed in the same popup (to avoid spamming)
'''
class DesktopMessage:
    def __init__(self, message, timeout):
        self.message = message
        self.expire = time.time() + timeout/1000.  # notify timeout is ms, not sec
