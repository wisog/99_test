from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'All is well!'


@app.after_request
def after_request(response):
    """
    Basically CORS middleware
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
    return response


if __name__ == '__main__':
    app.run()
