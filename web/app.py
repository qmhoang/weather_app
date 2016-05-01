import requests, re, requests.auth, json, time

from flask import Flask, redirect, request, render_template, session

app = Flask(__name__)
app.config['USER_SERVICE_URL'] = 'http://192.168.99.100:5000'
# app.config['LOCATION_SERVICE_URL'] = 'http://192.168.99.100:5001'
app.config['LOCATION_SERVICE_URL'] = 'http://localhost:5001'
app.secret_key = 'really secret key'


@app.route('/', methods=['GET'])
def index():
    token = get_token()

    if token is None:
        return render_template('login.html')
    else:
        locations = requests.get(app.config['LOCATION_SERVICE_URL'] + '/api/me/location', headers=token).json()
        weathers = []
        for l in locations:
            city_weather = requests.get(app.config['LOCATION_SERVICE_URL'] + '/api/weather/{}'.format(l['id']),
                                        headers=token).json()
            print(city_weather)
            weathers.append(city_weather)

        return render_template('/main.html', weathers=weathers)


@app.route('/login', methods=['POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        r = requests.get(app.config['USER_SERVICE_URL'] + '/api/token',
                         auth=requests.auth.HTTPBasicAuth(username, password))

        if r.status_code == 200:
            session['token'] = r.json()['token']
            return redirect('/')
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)


@app.route('/settings', methods=['GET'])
def settings():
    token = get_token()

    if token is None:
        return render_template('/login.html', error='session has expired')

    user = requests.get(app.config['USER_SERVICE_URL'] + '/api/me', headers=token).json()
    locations = requests.get(app.config['LOCATION_SERVICE_URL'] + '/api/me/location', headers=token).json()
    return render_template('settings.html', user=user['username'], id=user['id'], locations=locations)


zipcode_pattern = re.compile('^[0-9]{5}$')


@app.route('/add_location', methods=['POST'])
def add_location():
    token = get_token()

    if token is None:
        return render_template('/login.html', error='session has expired')

    if request.method == 'POST':
        address = request.form['address']

        if zipcode_pattern.search(address) is not None:
            requests.post(app.config['LOCATION_SERVICE_URL'] + '/api/me/location',
                          data={'address': address, 'address_type': 'ZIPCODE'}, headers=token)
        else:
            requests.post(app.config['LOCATION_SERVICE_URL'] + '/api/me/location',
                          data={'address': address, 'address_type': 'CITY_COUNTRY'}, headers=token)
    return redirect('/settings')


@app.route('/delete_location', methods=['POST'])
def delete_location():
    token = get_token()

    if token is None:
        return render_template('/login.html', error='session has expired')

    if request.method == 'POST':
        locations = [item for item in request.values.items(multi=True)]

        for l in locations:
            requests.delete(app.config['LOCATION_SERVICE_URL'] + '/api/location/{}'.format(l[1]), headers=token)

    return redirect('/settings')


def get_token():
    if session['token'] is not None:
        return {'Authorization': 'token ' + session['token']}
    else:
        return None


@app.route('/logout', methods=['GET'])
def logout():
    session['token'] = None
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
