import glib, gobject
import BaseHTTPServer, re

class GlibMixin:
    def watch_cb(self, source, cond):
        self._handle_request_noblock()
        return True

    def start(self):
        glib.io_add_watch(self, glib.IO_IN, self.watch_cb)


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        print self.request
        fetch_m = re.match("^/fetch/([0-9]+)", self.path)
        if self.path == "/version":
            self.send_response(200)
            self.end_headers()
            self.request.send("0\n")
        elif fetch_m:
            # Would be nice to use sendfile()
            self.send_response(200)
            self.end_headers()
            # TODO: send headers so this data gets written to disk with the right filename etc
            self.request.sendall(open(self.server.files[int(fetch_m.group(1))]).read())
        else:
            self.send_error(404, "Unknown method: %s\n" % self.path)

    def do_POST(self):
        if self.path == "/request":
            pass
        else:
            self.send_error(404, "Unknown method: %s\n" % self.path)

class Server(GlibMixin, BaseHTTPServer.HTTPServer):
    def __init__(self):
        BaseHTTPServer.HTTPServer.__init__(self, ("", 8080), Handler)
        self.files = {}
        self.counter = 0

    def add_file(self, filename):
        self.counter = self.counter + 1
        self.files[self.counter] = filename
        return self.counter

if __name__ == "__main__":
    httpd = Server()
    httpd.start()
    print httpd.add_file("/home/ross/Mess/barf/barf.py")
    gobject.MainLoop().run()
