import requests

from cerberus import Validator
from flask import Flask
from flask import request

app = Flask(__name__)
schema = {
    ';)': {'type': 'string', 'required': True},
    ';)': {'type': 'string', 'required': True}
}
v = Validator(schema)


@app.route('/', methods=['POST'])
def index():
    v.validate(request.json)
    url = ';)'
    response = requests.post(url, json=request.json)
    return response.json()


if __name__ == '__main__':
    app.run(debug=True)
