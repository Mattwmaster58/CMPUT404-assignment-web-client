#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, Mattwaster58 https://github.com/tywtyw2002, and https://github.com/treedust
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

import re
import socket
import sys
from _socket import SHUT_WR
# you may use urllib to encode data appropriately

from dataclasses import dataclass, field
from typing import Dict, Any
from urllib.parse import urlparse, quote, urlencode


def help():
    print("httpclient.py [GET/POST] [URL]\n")


@dataclass
class HTTPResponse:
    code: int = 200
    body: str = ""


class HTTPRequest:
    METHOD = ...
    VERSION = "1.1"

    def __init__(self, url: str, headers: Dict[str, Any] = None, body: str = ""):
        self.body = body
        parsed = urlparse(url)
        self.port = parsed.port or 80
        self.host = parsed.netloc.split(":")[0] # netloc != host, apparently. chop port off netloc
        self.path = quote(parsed.path)
        self.headers = {
            **(headers or {}),
            # virtual hosting support
            "Host": self.host,
            "Connection": "close",
            "Upgrade-Insecure-Requests": 0,  # i like insecurity
            "Accept": "*/*",  # don't think this matters, but why not
        }

    @property
    def serialized(self):
        # urlparse will make path empty? not sure whose fault that is
        lines = [f"{self.METHOD} {self.path or '/'} HTTP/{self.VERSION}"]
        for key, val in self.headers.items():
            lines.append(f"{key}: {val}")
        lines.append("")
        if self.body:
            lines.append(self.body)
        return "\r\n".join(lines)


class POSTRequest(HTTPRequest):
    METHOD = "POST"

    def __init__(self, url: str, headers: Dict[str, Any] = None, vars: Dict[str, Any] = None):
        body = urlencode(vars)
        super().__init__(url, headers, body)
        self.headers.update({
            # POST should send content length regardless of body.
            "Content-Length": len(self.body),
            "Content-Type": "application/x-www-url-encoded",
        })


class GETRequest(HTTPRequest):
    METHOD = "GET"

    def __init__(self, url: str):
        super().__init__(url, {}, "")


class HTTPClient:
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if part:
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url):
        request = GETRequest(url)
        self.connect(request.host, request.port)
        self.sendall(request.serialized)
        self.socket.shutdown(SHUT_WR)
        raw_resp = self.recvall()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url)


if __name__ == "__main__":
    client = HTTPClient()
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
