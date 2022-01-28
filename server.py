#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Copyright 2022 Zihan Su
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

message_404 = "<html><head><title>404 Not Found</title></head><body><h1>Not Found</h1>\
            <p>The requested URL /t.html was not found on this server.</p></body></html>"

message_405 = "<html><head><title>405 Method Not Allowed</title></head><body><h1>Method Not Allowed</h1>\
            <p>The requested URL /t.html was not allowed on this server.</p></body></html>"

message_301 = "<html><head><title>301 Moved Permanently</title></head><body><h1>Moved Permanently</h1>\
            <p>The requested URL /t.html was moved permanently on this server.</p></body></html>"

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.host_port = self.data.decode('utf-8').split('\n')[2].split()[1]
        #print ("Got a request of: %s\n" % self.data.decode('utf-8'))

        #check methods
        self.method = self.data.decode('utf-8').split()[0]
        if self.method != 'GET':
            self.method_not_allowed_405()
        else:
            #check path
            self.path = 'www' + self.data.decode('utf-8').split()[1]
            if not self.is_safe_path(self.path):
                self.path_not_found_404()
            else:
                if os.path.isdir(self.path):
                    self.handle_dir(self.path)
                elif os.path.isfile(self.path):
                    self.handle_file(self.path)
                else:
                    self.path_not_found_404()

        #self.request.sendall(bytearray("OK",'utf-8'))

    def path_not_found_404(self):
        response = f'HTTP/1.1 404 Not Found\r\nServer: zihansu\r\nContent-Type: text/html\r\nContent-Length: {len(message_404)}\r\nConnection: Closed\r\n\r\n'
        self.request.sendall(bytearray(response,'utf-8'))

    def method_not_allowed_405(self):
        response = f'HTTP/1.1 405 Method Not Allowed\r\nServer: zihansu\r\nContent-Type: text/html\r\nContent-Length: {len(message_405)}\r\nConnection: Closed\r\n\r\n'
        self.request.sendall(bytearray(response,'utf-8'))

    def moved_permanently_301(self):
        location = 'http://' + self.host_port + self.data.decode('utf-8').split()[1] + '/'
        response = f"HTTP/1.1 301 Moved Permanently\r\nServer: zihansu\r\nContent-Type: text/html\r\nContent-Length: {len(message_301)}\r\nConnection: closed\r\n\r\nLocation: {location}\r\n"
        #print(response)
        self.request.sendall(bytearray(response,'utf-8'))       

    def is_safe_path(self, path):
        basedir = os.path.abspath('www')
        matchpath = os.path.realpath(path)
        return basedir == os.path.commonpath((basedir, matchpath))


    def handle_dir(self, path):
        if path[-1] == '/':
            path += 'index.html'
            if os.path.isfile(path):
                file = open(path, 'r')
                content = file.read()
                file.close()
                response = f'HTTP/1.1 200 OK\r\nServer: zihansu\r\nContent-Type: text/html\r\nContent-Length: {len(content)}\r\nConnection: Closed\r\n\r\n{content}\r\n'
                self.request.sendall(bytearray(response,'utf-8'))
            else:
                self.path_not_found_404()
        else:
            # 301 - correct paths
            path += '/'
            self.moved_permanently_301()

    def handle_file(self, path):
        file = open(path)
        content = file.read()
        file.close()
        content_type = self.check_type(path) 
        response = f'HTTP/1.1 200 OK\r\nServer: zihansu\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\nConnection: Closed\r\n\r\n{content}\r\n'
        self.request.sendall(bytearray(response,'utf-8'))

    
    def check_type(self, path):
        type = None
        if path.endswith('.html'):
            type = 'text/html'
        if path.endswith('.css'):
            type = 'text/css'
        return type
    

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
