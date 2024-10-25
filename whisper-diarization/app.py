from flask import Flask, jsonify
import py_eureka_client.eureka_client as eureka_client
import os
from datetime import datetime
app = Flask(__name__)

@app.route("/")
def web():
    return """
    <p>Hola Marzzio, no se usar Flask</p>
"""

eureka_client.init(
    eureka_server = "http://localhost:8761/eureka",
    app_name="python-microservice",
    instance_port =5000,
    instance_host ="localhost"
)