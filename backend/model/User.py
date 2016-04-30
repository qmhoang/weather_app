from alchy import ModelBase, make_declarative_base
from sqlalchemy import orm, Column, types
from passlib.hash import sha256_crypt

Model = make_declarative_base()


class User(Model):
    __tablename__ = 'users'

    id = Column(types.Integer, primary_key=True)
    username = Column(types.String(80), unique=True)  # probably should be email
    password_hash = Column(types.String(256))  # needs to be salted in the future, unsalted right now

    def __init__(self, username, password):
        Model.__init__(self)
        self.username = username
        self.password_hash = sha256_crypt.encrypt(password)

    def verify_pass(self, password):
        return sha256_crypt.verify(password, self.password_hash)