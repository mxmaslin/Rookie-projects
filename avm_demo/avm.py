import os
import json
import requests
import time

from cerberus import Validator
from flask import Flask, request, render_template
from selenium.webdriver.support.ui import Select
from selenium import webdriver


app = Flask(__name__)

schema = {
    'postcode': {'type': 'string', 'required': True},
    'huisnummer': {'type': 'string', 'required': True},
    'huisnummer_toevoeging': {'type': 'string', 'required': False}
}
v = Validator(schema)

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get(
    'GOOGLE_CHROME_BIN', '/app/.apt/usr/bin/google-chrome'
)
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
browser = webdriver.Chrome(
    executable_path=os.environ.get(
        'CHROMEDRIVER_PATH', '/app/.chromedriver/bin/chromedriver'
    ),
    chrome_options=chrome_options
)


def conv(string):
    dig = 0
    ok = 0
    last = 10
    for i in string:
        if '0' <= i <= '9':
            if ok:
                dig= dig + (int(i) / last)
                last *= 10
            else:
                dig = dig * 10 + int(i)
        elif i == ',':
            ok = 1
    return dig


@app.route('/avm/', methods=['POST', 'GET'])
def index():
    url = 'https://mopsus.altum.ai/api/v1/altum/avm'
    message = []
    response_json = ''

    postcode = ''
    huisnummer = ''
    huisnummer_toevoeging = ''

    if request.method == 'POST':
        postcode = request.form.get('postcode', '')
        huisnummer = request.form.get('huisnummer', '')
        huisnummer_toevoeging = request.form.get('huisnummer_toevoeging', '')

        if not postcode:
            message.append('postcode is required.')

        if not huisnummer:
            message.append('huisnummer is required.')

        if message:
            message = ' '.join(message)

        payload = {
            'postcode': postcode,
            'housenumber': huisnummer,
            'houseaddition': huisnummer_toevoeging
        }
        response = requests.post(url, json=payload)
        response_json = response.json()

    return render_template(
        'test.html',
        message=message,
        response_json=response_json,
        postcode=postcode,
        huisnummer=huisnummer,
        huisnummer_toevoeging=huisnummer_toevoeging
    )


@app.route('/avm/api/', methods=['POST'])
def api():
    v.validate(request.json)
    payload = {
        'postcode': request.json['postcode'],
        'housenumber': request.json['huisnummer'],
        'houseaddition': request.json.get('huisnummer_toevoeging', '')
    }
    url = 'https://mopsus.altum.ai/api/v1/altum/avm'
    response = requests.post(url, json=payload)
    return response.json()


@app.route('/')
def query_example():
    language = request.args.get('language')
    return f'<h1>The language value is: {language}</h1>'


@app.route('/api')
def form_example():
    postcode = request.args.get('postcode', '3705LE')
    huisnummer = request.args.get('huisnummer', 74)
    geschatte_waarde = request.args.get('geschatte_waarde', 500000)
    validatie = request.args.get('validatie', 0)
    verhuurd = request.args.get('verhuurd', 0)
    verbouwing = request.args.get('verbouwing', 0)
    nieuwbouw = request.args.get('nieuwbouw', 0)
    soort_woning = request.args.get('soort_woning', 'appartement')

    # browser = webdriver.Chrome('C:/chromedriver/chromedriver.exe')
    url = 'https://www.support4tp.nl/aanvraag/nieuw/type/woningtaxatie'
    browser.get(url)

    Object_Postcode = browser.find_element_by_id('Object_Postcode')
    Object_Huisnummer = browser.find_element_by_id('Object_Huisnummer')
    Object_GeschatteWaarde = browser.find_element_by_id(
        'Object_GeschatteWaarde')
    Object_Type = browser.find_element_by_id('Object_Type')

    # appartement
    # woonhuis
    value = ''

    if soort_woning == 'woonhuis':
        if not (verhuurd or verbouwing or nieuwbouw):
            value = 'Woonhuis&Nieuwbouw'
        if nieuwbouw and not (verhuurd or verbouwing):
            value = 'Woonhuis'
        if verhuurd and not (verbouwing or nieuwbouw):
            value = 'Woonhuis&Verbouwing&In verhuurde staat'
        if verbouwing and not (verhuurd or nieuwbouw):
            value = 'Woonhuis&Verbouwing'
        if verhuurd and verbouwing and not nieuwbouw:
            value = 'Woonhuis&In verhuurde staat'

    if soort_woning == 'appartement':
        if nieuwbouw and not (verhuurd or verbouwing):
            value = 'Appartement&Nieuwbouw'
        if not (verhuurd or verbouwing or nieuwbouw):
            value = 'Appartement'
        if verhuurd and not (verbouwing or nieuwbouw):
            value = 'Appartement&In verhuurde staat'
        if verbouwing and not (verhuurd or nieuwbouw):
            value = 'Appartement&Verbouwing'
        if verhuurd and verbouwing and not nieuwbouw:
            value = 'Appartement&Verbouwing&In verhuurde staat'

    Object_Postcode.send_keys(postcode)
    Object_Huisnummer.send_keys(huisnummer)
    Object_GeschatteWaarde.send_keys(geschatte_waarde)

    select = Select(browser.find_element_by_id('Object_Type'))
    select.select_by_value(value)

    time.sleep(5)

    ans = {'status': 404}
    try:
        Object_Postcode.submit()
    except:
        return json.dumps(ans)

    time.sleep(5)

    if validatie == 0:
        btn = browser.find_element_by_xpath(
            '//*[@id="fieldset-Taxateur"]/div[1]/div/label[1]'
        )
        btn.click()

    time.sleep(2)

    wrap = browser.find_element_by_xpath(
        '//*[@id="fieldset-Taxateur"]/div[3]/div'
    )
    ele = wrap.find_elements_by_tag_name('label')
    li = []
    for cnt, i in enumerate(ele, start=1):
        dic = {
            'name': i.find_element_by_xpath(
                f'//*[@id="fieldset-Taxateur"]/div[3]/div/label[{str(cnt)}]/span[1]'
            ).text,
            'price': conv(
                i.find_element_by_xpath(
                    f'//*[@id="fieldset-Taxateur"]/div[3]/div/label[{str(cnt)}]/span[4]'
                ).text
            )
        }
        li.append(dic)
    browser.quit()

    ans = {'status': 200, 'value': li}
    return json.dumps(ans)


if __name__ == '__main__':
    app.run(debug=True)
