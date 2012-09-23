import string, cgi, time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser
from multiprocessing import Process
import os, time


def get_handler(id):
    class HagridHandler(BaseHTTPRequestHandler):
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
                    self.wfile.write("</body></html>")
                    return
                else:
                    return
            except IOError:
                self.send_error(404, 'File Not Found: {}'.format(self.path))
    return HagridHandler


def create_process(id, port):
    def fork_main():
        server = HTTPServer(('', port), get_handler(id))
        print "Started http server {}, port {}".format(id, port)
        server.serve_forever()
    process = Process(target=fork_main, args=())
    process.start()
    return process


def main():
    parser = OptionParser()
    parser.add_option("-m", "--multi", dest="multi", default="1", metavar="XXXX")
    parser.add_option("-p", "--port", dest="port", default="8080", metavar="XXXX")
    (options, args) = parser.parse_args()

    servers = []
    for i in xrange(int(options.multi)):
        servers.append(create_process(i, int(options.port) + i))

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


