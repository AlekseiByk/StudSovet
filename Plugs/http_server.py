import http.server
import logging

addr = "0.0.0.0"
port = 8000
secret = ''

logger = logging.getLogger("Plugs")

# ensure dual-stack is not disabled; ref #38907
class DualStackServer(http.server.ThreadingHTTPServer):
    def server_bind(self):
        # suppress exception when protocol is IPv4
        with http.server.contextlib.suppress(Exception):
            self.socket.setsockopt(
                http.server.socket.IPPROTO_IPV6, http.server.socket.IPV6_V6ONLY, 0)
        return super().server_bind()

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):                   #Heandler for GET Reguest 
    def do_GET(self):
        self.send_response(http.server.HTTPStatus.NOT_FOUND)
    def do_POST(self):
        if not self.path == ('/' + secret):
            self.send_response(http.server.HTTPStatus.NOT_FOUND)
            return
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = post_data.decode('ascii')
        if data.split('=')[0] == 'finished':
            washer = int( data.split('=')[1])
            #TODO send notification to user
        else:
            washer = int( data.split('=')[1])
            logger.info(f"washer {washer : 02} - " + data.split('=')[0])
        self.send_response(http.server.HTTPStatus.OK)
        self.end_headers()

def set_logger(logger: logging.Logger, filename):
    format = "%(asctime)s >>> %(message)s"
    logging.basicConfig(level=logging.INFO, format=format)
#    filehand = logging.FileHandler(f"/home/admin/ssFRKT-bot/logs/{filename}")
    filehand = logging.FileHandler(f"{filename}") 
    filehand.setFormatter(logging.Formatter(format))
    logger.addHandler(filehand)

def run():
    set_logger(logger, "http_server.log")
    server_addr = (addr, port)
    httpd = DualStackServer(server_addr,MyRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == "__main__":
    run()
