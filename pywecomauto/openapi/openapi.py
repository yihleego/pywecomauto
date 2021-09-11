# -*- coding: utf-8 -*-
from flask import Flask, request

from pywecomauto.openapi import server_port
from pywecomauto.openapi.service import handle

app = Flask('openapi')


@app.post("/")
def gateway():
    return handle(request.json)


@app.post("/test")
def test():
    print(request.json)
    return request.json


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=server_port)
