from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import cgi, json, codecs, requests, time, threading
from socketserver import ThreadingMixIn

def getLog():
    return json.loads(open("logging.json").read())

def logInfo(info):
    log = getLog()
    log.append(info)
    open("logging.json", "w").write(json.dumps(log))

class RestHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(getLog()).encode())
    def do_POST(self):
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()
        data = json.loads(self.data_string)
        logInfo(data)

httpd = HTTPServer(('0.0.0.0', 9000), RestHTTPRequestHandler)
httpd.serve_forever()