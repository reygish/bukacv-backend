from flask import Flask, jsonify
from endpoints import api_bp

app = Flask(__name__)

app.register_blueprint(api_bp)

@app.route('/')
def home():
    return jsonify(message="Hello from Flask!")

@app.route('/about')
def about():
    return jsonify(status="Success", framework="Flask")

