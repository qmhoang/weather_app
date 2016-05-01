from alchy import make_declarative_base
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)
from passlib.hash import sha256_crypt
from sqlalchemy import Column, types, ForeignKey, Enum, UniqueConstraint

Model = make_declarative_base()


class User(Model):
    __tablename__ = 'users'

    id = Column(types.Integer, primary_key=True)
    username = Column(types.String(80), unique=True)  # probably should be email
    password_hash = Column(types.String(256), nullable=False)  # needs to be salted in the future, unsalted right now

    def __init__(self, username, password):
        Model.__init__(self)
        self.username = username
        self.password_hash = sha256_crypt.encrypt(password)

    def set_pass(self, password):
        self.password_hash = sha256_crypt.encrypt(password)

    def verify_pass(self, password):
        return sha256_crypt.verify(password, self.password_hash)

    def gen_auth_token(self, serializer):
        return serializer.dumps({'id': self.id})

        
class Location(Model):
    __tablename__ = 'sites'

    id = Column(types.Integer, primary_key=True, nullable=False)
    user_id = Column(types.Integer, ForeignKey('users.id'), index=True, nullable=False)
    address_type = Column(Enum("LAT_LONG", "CITY", "CITY_COUNTRY", "ZIPCODE", name="address_type"), nullable=False)
    address = Column(types.String(50), nullable=False)  # could be zip code, city, lat & long, whatever
    UniqueConstraint(user_id, address_type, address)
