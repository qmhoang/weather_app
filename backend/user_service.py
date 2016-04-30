from flask import Flask, request, abort, jsonify, url_for
from flask_alchy import Alchy
from model.User import Model, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pass@192.168.99.101:5432/postgres'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = Alchy(app, Model=Model)

db.create_all()


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        print("user: bad request")
        return jsonify({}), 400  # bad request
    if User.query.filter_by(username=username).first() is not None:
        print("username already exist")
        return jsonify({}), 400  # already exist

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'username': user.username}), 201, {'Location': url_for('get_user', id=user.id, _external=True)}


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

if __name__ == '__main__':
    app.run(debug=True)