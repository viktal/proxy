from socketserver import BaseRequestHandler, ThreadingTCPServer
import logging
import subprocess
from random import random
import socket
import ssl
import os
import http_parser
import config
from http_parser.http import HttpStream
from http_parser.reader import SocketReader
from data_base import Request, Session
from join_headers import join_data

CON_ESTABLISH = b'HTTP/1.0 200 Connection established\r\n\r\n'


class Handler(BaseRequestHandler):
    def handle(self):
        self.logger = logging.getLogger("proxy")
        self.session = Session()
        try:
            request = HttpStream(SocketReader(self.request))
            _ = request.status()
        except http_parser.http.BadStatusLine:
            return

        self.logger.warning(request.path())

        if 'CONNECT' == request.method():
            self.https_proxy(request)
        else:
            self.http_proxy(request)

        self.session.close()

    def generate_cert(self, host: str):
        path = f'certs/{host}.crt'
        if not os.path.exists(path):
            with open(path, 'w') as f:
                subprocess.call(['./gen_cert.sh', host, str(int(random() * 1000000000))], stdout=f)
            self.logger.info(f'Certificate to {host} generated')
        return path

    def https_proxy(self, connectreq: HttpStream):
        self.request.sendall(CON_ESTABLISH)

        host, port = connectreq.path().split(':')
        cert_path = self.generate_cert(host)

        # request to localhost as server
        try:
            sock_client = ssl.wrap_socket(self.request, keyfile="cert.key", certfile=cert_path,
                                          ssl_version=ssl.PROTOCOL_TLS, server_side=True)
            sock_server = socket.create_connection((host, port))
            sock_server = ssl.create_default_context().wrap_socket(sock_server, server_hostname=host)
        except OSError:
            return

        client_reader = SocketReader(sock_client)
        server_reader = SocketReader(sock_server)
        while True:
            # request to mail.ru as client
            clientreq = HttpStream(client_reader, decompress=True)
            try:
                clientreq_tosend = join_data(clientreq, 'Request')
            except (http_parser.http.ParserError, http_parser.http.BadStatusLine, ConnectionResetError):
                return

            sock_server.sendall(clientreq_tosend)

            # request from mail.ru to localhost as client
            server_resp = HttpStream(server_reader, decompress=True)
            try:
                server_resp_tosend = join_data(server_resp, 'Response')
            except (http_parser.http.ParserError, http_parser.http.BadStatusLine, ConnectionResetError):
                return
            try:
                sock_client.sendall(server_resp_tosend)
            except BrokenPipeError:
                return

            req = Request(clientreq.method(), server_resp.status_code(), clientreq_tosend, host)
            self.add_date_base(clientreq, req)

    def add_date_base(self, request: HttpStream, row_request: Request):
        if 'Content-Type' in request.headers() or 'content-type' in request.headers():
            if request.headers()['Content-Type'].lower().startswith(config.CONTENT_TYPES):
                self.session.add(row_request)
                self.session.commit()

    def http_proxy(self, connectreq: HttpStream):
        reqheaders = connectreq.headers()
        # if ":" in connectreq.path():
        parsed_url = connectreq.url().split('//')[1].split(':')
        if len(parsed_url) > 1:
            host = parsed_url[0]
            port = parsed_url[1].split('/')[0]
        else:
            host, port = reqheaders['host'], 80
        if 'Proxy-Connection' in reqheaders:
            del reqheaders['Proxy-Connection']
        elif 'proxy-connection' in reqheaders:
            del reqheaders['proxy-connection']

        # request to mail.ru as client
        sock_server = socket.create_connection((host, port))
        try:
            clientreq = join_data(connectreq, 'Request')
        except (http_parser.http.ParserError, http_parser.http.BadStatusLine, ConnectionResetError):
            return

        sock_server.sendall(clientreq)

        # request from mail.ru to localhost as client
        if connectreq.method() == 'HEAD':
            return
        server_reader = SocketReader(sock_server)
        server_resp = HttpStream(server_reader, decompress=True)
        try:
            server_resp_tosend = join_data(server_resp, 'Response')
        except (http_parser.http.ParserError, http_parser.http.BadStatusLine, ConnectionResetError):
            return
        self.request.sendall(server_resp_tosend)

        req = Request(connectreq.method(), server_resp.status_code(), clientreq, host)
        self.add_date_base(connectreq, req)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    ThreadingTCPServer.allow_reuse_address = True
    with ThreadingTCPServer(config.SERVER_ADDRESS, Handler) as server:
        server.serve_forever()
        logging.info(f'Proxy-server start on {config.SERVER_ADDRESS}')
