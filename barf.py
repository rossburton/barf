#! /usr/bin/env python

import avahi, dbus, gobject
from zeroconf import ZeroconfService

from dbus.mainloop.glib import DBusGMainLoop
loop = DBusGMainLoop(set_as_default=True)

bus = dbus.SystemBus()
avahi_daemon = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
                              avahi.DBUS_INTERFACE_SERVER)

def get_service_name():
    """
    Get the mDNS service name for this barf instance, such as "ross on
    flashheart".  Should be improved to use the user's full name, ensure that it
    uses the full name on OS X, i18n, and so on.
    """
    import platform, getpass
    return "%s on %s" % (getpass.getuser(), platform.node())

def publish():
    """
    Announce ourselves over mDNS.  Custom service type, but we're just HTTP
    really.
    """
    
    # TODO: do properly in http.py
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    addr, port = s.getsockname()
    print "Got port %d" % port

    # TODO: find a spare port when creating server, use that here
    zeroconf = ZeroconfService(name=get_service_name(),
                               port=port,
                               stype="_barf._tcp")


def on_new_service(interface, protocol, name, type, domain, flags):
    if flags & avahi.LOOKUP_RESULT_OUR_OWN:
        print "Ignoring %s" % name
        return
    print "Found %s" % name

def on_remove_service(interface, protocol, name, type, domain, flags):
    print "Lost %s" % name

def search():
    browser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
                                            avahi_daemon.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, "_barf._tcp", "", dbus.UInt32(0))),
                             avahi.DBUS_INTERFACE_SERVICE_BROWSER)
    browser.connect_to_signal('ItemNew', on_new_service)
    browser.connect_to_signal('ItemRemove', on_remove_service)

def main():
    publish()
    search()

if __name__ == "__main__":
    main()
    gobject.MainLoop().run()
