import avahi, dbus

# TODO: copyright, debug mode

class ZeroconfService:
    def __init__(self, name, port, stype,
                 domain="", host="", text=""):
        self.name = name
        self.domain = domain
        self.stype = stype
        self.host = host
        self.port = port
        self.text = text

        self.group = None
        self.n_rename = 0

        self.bus = dbus.SystemBus()
        self.server = dbus.Interface(
            self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
            avahi.DBUS_INTERFACE_SERVER)
        
        self.server.connect_to_signal("StateChanged", self.server_state_changed)
        self.server_state_changed(self.server.GetState())

    def server_state_changed(self, state):
        if state == avahi.SERVER_COLLISION:
            # TODO: find out semantics of this...
            print "WARNING: Server name collision"
            self.unpublish()
        elif state == avahi.SERVER_RUNNING:
            print "server running"
            # TODO: only publish if we've been told to, to allow delayed init
            self.publish()

    def entry_group_state_changed(self, state, error):
        global name, server, n_rename

        if state == avahi.ENTRY_GROUP_ESTABLISHED:
            print "Service established."
        elif state == avahi.ENTRY_GROUP_COLLISION:
            self.n_rename = self.n_rename + 1
            if self.n_rename >= 5:
                print "ERROR: No suitable service name found after %i retries, exiting." % n_rename
            else:
                self.name = self.server.GetAlternativeServiceName(self.name)
                print "WARNING: Service name collision, changing name to '%s' ..." % self.name
                self.remove_service()
                self.add_service()

    def publish(self):
        print "publishing"
        if self.group is None:
            self.group = dbus.Interface(
                self.bus.get_object(avahi.DBUS_NAME,
                                    self.server.EntryGroupNew()),
                avahi.DBUS_INTERFACE_ENTRY_GROUP)
            self.group.connect_to_signal('StateChanged', self.entry_group_state_changed)
        assert self.group.IsEmpty()
        
        # TODO only if we're running, otherwise set a flag for server_state_changed()
        try:
            self.group.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, dbus.UInt32(0),
                                  self.name, self.stype, self.domain, self.host,
                                  dbus.UInt16(self.port), avahi.string_array_to_txt_array(self.text))
            self.group.Commit()
        except dbus.exceptions.DBusException, e:
            print e
            # TODO: this exception is bad
            print "FAIL"
            self.name = self.server.GetAlternativeServiceName(self.name)
            self.publish()

 
    def unpublish(self):
        if not self.group is None:
            self.group.Reset()
 
 
def test():
    service = ZeroconfService(name="ZeroConfTestService", port=1234, stype="_foo._tcp")
    raw_input("Press any key to unpublish the service")
    service.unpublish()
    raw_input("Press any key to exit the test")
  
if __name__ == "__main__":
    from dbus.mainloop.glib import DBusGMainLoop
    loop = DBusGMainLoop(set_as_default=True)
    test()
