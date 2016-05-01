import re, requests, json

from flask import Flask, g
from flask_alchy import Alchy
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_httpauth import HTTPTokenAuth
from model.User import Model, Location

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-me-location!!!!!'
# app.config['USER_SERVICE_URL'] = 'http://user_service:5000/api/me'
# app.config['HOST'] = '0.0.0.0'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/postgres'
app.config['USER_SERVICE_URL'] = 'http://192.168.99.100:5000/api/me'
app.config['HOST'] = '127.0.0.1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@192.168.99.100:5432/postgres'
app.config['OPENWEATHERMAP_SERVICE_URL'] = 'http://api.openweathermap.org/data/2.5/weather'
app.config['OPENWEATHERMAP_API_KEY'] = '0c77231223df5bae357bd2bd85104554'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = Alchy(app, Model=Model)
db.create_all()

api = Api(app)

auth = HTTPTokenAuth(scheme='Token')

location_parser = reqparse.RequestParser()
location_parser.add_argument('address_type', required=True, help='address_type cannot be blank')
location_parser.add_argument('address', required=True, help='address cannot be blank')

location_get_parser = reqparse.RequestParser()
location_get_parser.add_argument('address_type', required=True, help='address_type cannot be blank', location='args')
location_get_parser.add_argument('address', required=True, help='address cannot be blank', location='args')

location_resource_fields = {
    'user_id': fields.String,
    'address_type': fields.String,
    'address': fields.String
}

zipcode_pattern = re.compile('^[0-9]{5}$')


@auth.verify_token
def verify_token(token):
    g.user = None

    resp = requests.get(app.config['USER_SERVICE_URL'], headers={'Authorization': 'token ' + token})

    print('status={}'.format(resp.status_code))
    if resp.status_code == 200:
        g.user = resp.json()
        return True
    else:
        return False


class LocationApi(Resource):
    decorators = [auth.login_required]

    # not really needed
    # @marshal_with(location_resource_fields)
    # def get(self):
    #     args = location_get_parser.parse_args()
    #
    #     address_type = args['address_type']
    #     address = args['address']
    #
    #     return Location.query.get((g.user['id'], address_type, address))

    def delete(self, id: int):
        pass


class MyLocationsApi(Resource):
    decorators = [auth.login_required]

    @marshal_with(location_resource_fields)
    def get(self):
        return Location.query.filter_by(user_id=g.user['id']).all()

    @marshal_with(location_resource_fields)
    def post(self):
        args = location_parser.parse_args()

        g_user_id = g.user['id']
        address_type = args['address_type']
        address = args['address']

        return post_location(g_user_id, g_user_id, address_type, address)


class UserLocationsApi(Resource):
    decorators = [auth.login_required]

    @marshal_with(location_resource_fields)
    def get(self, user_id):
        g_user_id = g.user['id']

        if user_id != g_user_id:
            abort(401)  # you don't have access

        return Location.query.filter_by(user_id=g.user['id']).all()

    @marshal_with(location_resource_fields)
    def post(self, user_id):
        args = location_parser.parse_args()

        g_user_id = g.user['id']

        if user_id != g_user_id:
            abort(401)  # you don't have access

        address_type = args['address_type']
        address = args['address']

        return post_location(g_user_id, user_id, address_type, address)


def post_location(g_user_id, user_id, address_type, address):
    if address_type == "ZIPCODE" and zipcode_pattern.search(address) is None:
        abort(400, message='invalid zip code format')

    location = Location(user_id=g_user_id, address_type=address_type, address=address)
    try:
        db.session.add(location)
        db.session.commit()
    except (IntegrityError, InvalidRequestError):
        db.session.rollback()
        abort(409, message='duplicate location')
    return location, 201


# local proxy, insert caching here
class Weather(Resource):
    def get(self):
        args = location_parser.parse_args()

        address_type = args['address_type']
        address = args['address']

        if address_type == "ZIPCODE":
            r = requests.get(app.config['OPENWEATHERMAP_SERVICE_URL'],
                             params={'zip': [address, 'us'], 'appid': app.config['OPENWEATHERMAP_API_KEY']})
            return r.json()

        abort(400)


api.add_resource(LocationApi, '/api/location')
api.add_resource(UserLocationsApi, '/api/<int:user_id>/location')
api.add_resource(MyLocationsApi, '/api/me/location')
api.add_resource(Weather, '/api/weather')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
