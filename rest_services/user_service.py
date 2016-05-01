from flask import Flask, g
from flask_alchy import Alchy
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from model.User import Model, User
from itsdangerous import TimedJSONWebSignatureSerializer as JWT

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-me-user!!!!!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/postgres'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = Alchy(app, Model=Model)
db.create_all()

api = Api(app)

auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Token')
jwt = JWT(app.config['SECRET_KEY'], expires_in=6000)

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', required=True, help='username cannot be blank')
user_parser.add_argument('password', required=True, help='password cannot be blank')

user_resource_fields = {
    'id': fields.Integer,
    'username': fields.String
}


class UserApi(Resource):
    @marshal_with(user_resource_fields)
    def get(self, id: int):
        user = User.query.get(id)
        if not user:
            abort(400, message='invalid id')
        return user, 200

    def delete(self, id: int):
        pass

    @marshal_with(user_resource_fields)
    def put(self, id: int):
        args = user_parser.parse_args()

        user = db.session.get(id)
        user.username = args['username']
        user.set_pass(args['password'])

        db.session.update(user)
        db.session.commit()

        return user, 201


class UsersApi(Resource):
    @marshal_with(user_resource_fields)
    def get(self):
        return User.query.all()

    @marshal_with(user_resource_fields)
    def post(self):
        args = user_parser.parse_args()

        username = args['username']
        password = args['password']

        if User.query.filter_by(username=username).first() is not None:
            abort(400, message="username already exist")

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return user, 201


class TokenApi(Resource):
    @auth.login_required
    def get(self):
        token = g.user.gen_auth_token(jwt)
        return {'token': token.decode('ascii')}, 200


class ValidToken(Resource):
    @token_auth.login_required
    @marshal_with(user_resource_fields)
    def get(self):
        return g.token_user


@auth.verify_password
def verify_pass(username, password):
    user = User.query.filter_by(username=username).first()

    if not user or not user.verify_pass(password):
        return False

    g.user = user
    return True


@token_auth.verify_token
def verify_token(token):
    g.token_user = None
    try:
        data = jwt.loads(token)
    except:
        return False

    user = User.query.get(data['id'])
    g.token_user = user
    return True


api.add_resource(UserApi, '/api/users/<int:id>')
api.add_resource(UsersApi, '/api/users')
api.add_resource(TokenApi, '/api/token')
api.add_resource(ValidToken, '/api/me')

if __name__ == '__main__':
    app.run(threaded=True, debug=True, host='0.0.0.0', port=5000)
