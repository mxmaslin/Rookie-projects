import requests

from cerberus import Validator
from flask import Flask
from flask import request


app = Flask(__name__)
schema = {
    'postcode': {'type': 'string', 'required': True},
    'huisnummer': {'type': 'string', 'required': True},
    'huisnummer_toevoeging': {'type': 'string', 'required': False}
}
v = Validator(schema)


@app.route('/', methods=['POST'])
def index():
    v.validate(request.json)
    payload = {
        'postcode': request.json['postcode'],
        'housenumber': request.json['huisnummer'],
        'houseaddition': request.json.get('huisnummer_toevoeging', '')
    }
    url = 'https://mopsus.altum.ai/api/v1/altum/avm'
    response = requests.post(url, json=payload)
    return response.json()


if __name__ == '__main__':
    app.run(debug=True)
