from cursa_acarreo import db, login_manager
import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(id):
    return User.find_by_id(id)


ROLES = ('operator', 'supervisor', 'admin')
class User(db.Document, UserMixin):
    """
    User Model
    """
    meta = {'collection': 'users',
            'indexes': [
                {'fields': ['username'],
                 'collation': {'locale': 'en', 'strength': 1  # Considers case and diactritics
                            }
                 },
                {'fields': ['email'],
                 'collation': {'locale': 'en', 'strength': 1  # Considers case and diactritics
                               }
                 }]}

    username = db.StringField(unique=True, required=True, max_length=25)
    hashed_pwd = db.StringField(required=True)
    name = db.StringField(max_length=50)
    last_name = db.StringField(max_length=50)
    email = db.EmailField(unique=True, sparse=True, max_length=100)
    role = db.StringField(required=True, choices=ROLES, default='operator')
    date_added = db.DateTimeField(required=True, default=datetime.datetime.utcnow())

    def json(self):
        skip_items = ['id', 'hashed_pwd']
        d_json = dict()
        for i in self:
            if i not in skip_items:
                if self[i] is None:
                    d_json[i] = ''
                else:
                    d_json[i] = self[i]
        return d_json

    def save_to_db(self):
        """
        Try to save instance. If there is an error, it reload info from DB to discard changes.
        :param self:
        :return:
        """
        try:
            self.save()
        except Exception as e:
            self.reload()
            raise e

    def set_password(self, password):
        self.hashed_pwd = generate_password_hash(password)
        self.save()

    def check_password(self, password):
        return check_password_hash(self.hashed_pwd, password)

    def update(self, **field_value):
        for fv in field_value:
            if fv == 'password':
                self.hashed_pwd = generate_password_hash(field_value['password'])
            elif fv == 'email' and field_value['email'] == '':
                self['email'] = None
            elif fv == 'email' or fv == 'username':
                self[fv] = field_value[fv].lower()
            else:
                self[fv] = field_value[fv]
        self.save_to_db()

    @classmethod
    def add(cls, username, password, email=None, name='', last_name='', role='operator'):
        email = None if (email == '' or email is None) else email.lower()
        return cls(username=username.lower(), hashed_pwd=generate_password_hash(password), email=email,
                   name=name, last_name=last_name, role=role).save()

    @classmethod
    def find_by_username(cls, username, raise_if_none=True):
        user = cls.objects(username__iexact=username).first()
        if not user and raise_if_none:
            raise NameError('Usuario {} no encontrado.'.format(username))
        return user

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()

    @classmethod
    def find_by(cls, field, value):
        return cls.objects(**{field: value})

    @classmethod
    def get_all(cls):
        return [u.json() for u in cls.objects]

    @classmethod
    def get_list_by(cls, param, lower=False):
        if lower:
            return [t[param].lower() if t[param] else t[param] for t in cls.objects]
        return [t[param] for t in cls.objects]


