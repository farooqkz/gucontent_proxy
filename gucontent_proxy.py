#!/usr/bin/python3
# Copyright (C) 2017 Farooq Karimi Zadeh <farooghkz at ompbx dot org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import socket
import threading
import requests
import gzip

PORT = 5433

class sockthread(threading.Thread):
    def __init__(self, csock):
        threading.Thread.__init__(self)
        self.csock = csock # client's socket
    def run(self):
        msg = self.csock.recv(1024).decode()
        if msg.startswith("GET"):
            url = msg.split(maxsplit=2)[1]
            if url.startswith("http"):
                api_url = "https://feedback.googleusercontent.com/gadgets/proxy"
                args = {"url": url, "container": "fbk"}
                req = requests.get(api_url, params=args, stream=True)
                bytes_ = req.raw.read()
                if bytes_[0] == 0x1f and bytes_[1] == 0x8b:
                    self.csock.send(gzip.decompress(bytes_))
                else:
                    self.csock.send(bytes_)
            else:
                self.csock.send(bytes("", "ascii"))
        else:
            self.csock.send(bytes("", "ascii"))
        self.csock.close()

sock = socket.socket()
sock.bind(("", PORT))
sock.listen()

try:
    while 1:
        sockthread(sock.accept()[0]).start()
except KeyboardInterrupt:
    print("Waiting for threads to terminate...")

while len(threading.enumerate()) > 1:
    pass
