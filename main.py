# -*- codeing = utf-8 -*-
import time, os, json
import flask
from flask import Flask, request, g, jsonify, make_response, render_template
from flask_cors import CORS
from functools import lru_cache
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
FOLDER = os.path.dirname(os.path.realpath(__file__))

@app.before_request
def _before_request():
    if "CF-Connecting-IP" in request.headers:
        flask.request.environ['REMOTE_ADDR'] = request.headers["CF-Connecting-IP"]
        try:
            import uwsgi
            uwsgi.set_logvar('cfip', request.headers["CF-Connecting-IP"])
        except:
            pass

if __name__ == "__main__":
    if os.getuid() != 0:
        app.run(host='0.0.0.0', port=3001)
