#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = self.get_headers(data).split(' ')[1]
        return int(code)

    def get_headers(self,data):
        headers = data.split('\r\n')[0]
        return headers

    def get_body(self, data):
        body = data.split('\r\n\r\n', 1)[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        print('url = ' + url)
        host, port, path = self.parseUrl(url)
        self.connect(host, port)
        req = self.constructReq('GET', host, path)
        self.sendall(req)
        recvMsg = self.recvall(self.socket)
        print(recvMsg)
        code = self.get_code(recvMsg)
        body = self.get_body(recvMsg)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        print('url = ' +url)
        host, port, path = self.parseUrl(url)
        self.connect(host, port)
        body = urllib.parse.urlencode(args) if args else ''
        req = self.constructReq('POST', host, path, body)
        self.sendall(req)
        recvMsg = self.recvall(self.socket)
        print(recvMsg)
        code = self.get_code(recvMsg)
        body = self.get_body(recvMsg)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    def parseUrl(self, url):
        urlComponents = urllib.parse.urlparse(url)
        host = urlComponents.hostname
        port = int(urlComponents.port) if urlComponents.port else 80
        path = urlComponents.path if urlComponents.path else '/'
        
        return host, port, path
    
    def constructReq(self, method, host, path, body=''):
        start_line = None
        length = len(body)
        if method == 'GET':
            start_line = '{} {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(method, path, host)
        elif method == 'POST':
            content_type = 'application/x-www-form-urlencoded'
            start_line = '{} {} HTTP/1.1\r\nHost: {}\r\nContent-Type: {}\r\nContent-Length: {}\r\nConnection: close\r\n\r\n'.format(
                method, path, host, content_type, length)
        
        return start_line + body

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
