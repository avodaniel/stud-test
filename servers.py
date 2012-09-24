import string, cgi, time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser
from multiprocessing import Process
import os, time, socket


def get_handler(id, header):
    class HagridHandler(BaseHTTPRequestHandler):
        def handle_one_request(self):
            self.stud_addr = ""
            if header:
                af_type = self.rfile.read(1)
                if ord(af_type[0]) == socket.AF_INET:
                    addr_packed = self.rfile.read(4)
                    addr = socket.inet_ntoa(addr_packed)
                    self.stud_addr=addr
            return BaseHTTPRequestHandler.handle_one_request(self)


        def do_GET(self):
            try:
                if self.path.endswith(".esp"):   #our dynamic content
                    self.send_response(200)
                    self.send_header('Content-type',	'text/html')
                    self.end_headers()

                    message = self.path[:-4]

                    self.wfile.write("<html><body>");
                    self.wfile.write("<h1>");
                    self.wfile.write("Id: <em>{}</em>".format(id));
                    self.wfile.write("</h1>");
                    self.wfile.write("<p>")
                    self.wfile.write(message)
                    self.wfile.write("</p>")
                    self.wfile.write("<div><small>")
                    self.wfile.write("Stud addr: <em>{}</em>".format(self.stud_addr))
                    self.wfile.write("</small></div>")
                    self.wfile.write("</body></html>")
                    return
                else:
                    return
            except IOError:
                self.send_error(404, 'File Not Found: {}'.format(self.path))
    return HagridHandler


def create_process(id, header, port):
    def fork_main():
        server = HTTPServer(('', port), get_handler(id, header))
        print "Started http server {}, port {}".format(id, port)
        server.serve_forever()
    process = Process(target=fork_main, args=())
    process.start()
    return process


def main():
    parser = OptionParser()
    parser.add_option("-m", "--multi", dest="multi", default="1", metavar="XXXX")
    parser.add_option("-p", "--port", dest="port", default="8080", metavar="XXXX")
    parser.add_option("-H", "--header", action="store_true", dest="header", metavar="XXXX")
    (options, args) = parser.parse_args()
    print "{!r}".format(options)
    servers = []
    for i in xrange(int(options.multi)):
        servers.append(create_process(i, options.header, int(options.port) + i))

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        print '^C received, shutting down servers'
    for server in servers:
        server.terminate()
        server.join()
        print "Server {} terminated".format()

if __name__ == '__main__':
    main()


