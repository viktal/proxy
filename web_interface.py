from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, desc
import config
from data_base import Request
import socket
import ssl
from http_parser.http import HttpStream
from http_parser.reader import SocketReader
from join_headers import join_data
import dirbuster

engine = create_engine(config.DATABASE_NAME)
session = scoped_session(sessionmaker(bind=engine))
app = Flask(__name__, static_url_path='/static')


@app.teardown_request
def remove_session(ex=None):
    session.remove()


@app.route('/requests/', methods=['get'])
def requests(error_message=None):
    req = session.query(Request).order_by(desc(Request.release_date)).limit(config.COUNT_REQUESTS).all()
    return render_template('requests.html', req=req, mes=error_message)


@app.route('/request/<int:req_id>/', methods=['get', 'post'])
def show_request(req_id):
    req = session.query(Request).filter(Request.id == req_id).limit(1).all()
    if len(req) == 0:
        return redirect(url_for('requests', error_message=f'Not found ID {req_id}'))
    req = req[0].headers.decode().split('\r\n')
    return render_template('request.html', req_id=req_id, req=req)


@app.route('/repeat/<int:req_id>/', methods=['get', 'post'])
def repeat_request(req_id):
    req = session.query(Request).filter(Request.id == req_id).limit(1).all()
    if len(req) == 0:
        return redirect(url_for('requests', error_message=f'Not found ID {req_id}'))
    req = req[0]
    sock_server = socket.create_connection((req.host, 443))
    sock_server = ssl.create_default_context().wrap_socket(sock_server, server_hostname=req.host)
    server_reader = SocketReader(sock_server)
    sock_server.sendall(req.headers)
    server_resp = HttpStream(server_reader, decompress=True)
    req = req.headers.decode().split('\r\n')
    answer = join_data(server_resp, 'Response')
    answer = answer.decode(errors='ignore')
    answer = answer.split('\r\n')
    return render_template('repeat.html', req_id=req_id, req=req, answer=answer)


@app.route('/scan/<int:req_id>/', methods=['get', 'post'])
def scan_request(req_id):
    req = session.query(Request).filter(Request.id == req_id).limit(1).all()
    if len(req) == 0:
        return redirect(url_for('requests', error_message=f'Not found ID {req_id}'))
    host = req[0].host
    result = dirbuster.dibuster(host)

    if type(result) is not list:
        return redirect(url_for('requests', error_message=f'Cannot scan. {result}'))
    return render_template('scan.html', host=host, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.WEB_PORT)
    session.close()
