from flask import request, Flask
from event_handler import event_handler


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST', 'HEAD', 'OPTIONS'])
def wrapper():
    return event_handler(request)


if __name__ == '__main__':
    app.run()
