from cursa_acarreo import db, login_manager
import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(id):
    return User.find_by_id(id)


class User(db.Document, UserMixin):
    """
    User Model
    """
    meta = {'collection': 'users'}
    username = db.StringField(unique=True, required=True, max_length=25)
    hashed_pwd = db.StringField(required=True)
    name = db.StringField(max_length=50)
    last_name = db.StringField(max_length=50)
    email = db.EmailField(unique=True, sparse=True, max_length=100)
    is_admin = db.BooleanField(required=True, default=False)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.utcnow())

    def json(self):
        skip_items = ['id', 'hashed_pwd']
        d_json = dict()
        for i in self:
            if i not in skip_items:
                d_json[i] = self[i]
        return d_json

    def set_password(self, password):
        self.hashed_pwd = generate_password_hash(password)
        self.save()

    def check_password(self, password):
        return check_password_hash(self.hashed_pwd, password)

    @classmethod
    def add(cls, username, password, email=None, name=None, last_name=None, is_admin=False):
        return cls(username=username, hashed_pwd=generate_password_hash(password), name=name.upper(),
                   last_name=last_name.upper(), email=email, is_admin=is_admin).save()

    @classmethod
    def find_by_username(cls, username, raise_if_none=True):
        user = cls.objects(username__iexact=username).first()
        if not user and raise_if_none:
            raise NameError('Usuario "{}" no encontrado.'.format(username))
        return user

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()

    @classmethod
    def get_all(cls):
        return [u.json() for u in cls.objects]

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]
