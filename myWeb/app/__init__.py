from flask import Flask
from app.route import hello_world, index

def create_app():
    app = Flask(__name__)
    app.add_url_rule('/', '/', hello_world)
    app.add_url_rule('/index', 'index', index)
    return app