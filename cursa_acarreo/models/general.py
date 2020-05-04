from cursa_acarreo import db
import datetime


class Driver(db.Document):
    """
    Driver model
    """
    meta = {'collection': 'drivers'}
    name = db.StringField(required=True, max_length=50)
    last_name = db.StringField(unique_with='name', required=True, max_length=50)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.now())

    @classmethod
    def add(cls, name, last_name):
        return cls(name=name, last_name=last_name).save()

    @classmethod
    def find_by_full_name(cls, name, last_name, raise_if_none=True):
        driver = cls.objects(name=name, last_name=last_name).first()
        if not driver and raise_if_none:
            raise NameError('Conductor "{}" no encontrado.'.format(name + " " + last_name))
        return driver


class Truck(db.Document):
    """
    Truck model
    """
    meta = {'collection': 'trucks'}
    id_code = db.StringField(required=True, unique=True, max_length=50)
    brand = db.StringField(required=False, max_length=50)
    plate = db.StringField(unique=True, sparse=True, max_length=50)
    capacity = db.IntField(required=False)
    driver = db.ReferenceField(Driver, reverse_delete_rule=db.NULLIFY)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.now())

    def json(self):
        skip_items = []
        d_json = dict()
        for i in self:
            if i not in skip_items:
                if i == 'driver' and self[i]:
                    d_json[i] = {'name': self[i].name, 'last_name': self[i].last_name}
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

    def _get_driver(self, name, last_name):
        driver = Driver.find_by_full_name(name, last_name)
        if not driver:
            raise db.ValidationError('El chofer "{}", que intenta agregar no esta dado de alta en el '
                                     'sistema'.format(name + " " + last_name))
        return driver

    def set_driver(self, name, last_name):
        driver = self._get_driver(name, last_name)
        self.driver = driver
        self.save_to_db()

    @classmethod
    def add(cls, id_code, brand=None, plate=None, capacity=None, driver_name=None):
        if driver_name:
            if not isinstance(driver_name, tuple):
                raise TypeError('Driver name must be a tuple with format ("name","last_name")')
            driver = cls()._get_driver(*driver_name)
        else:
            driver = driver_name
        return cls(id_code=id_code, brand=brand, plate=plate,capacity=capacity, driver=driver).save()

    @classmethod
    def find_by_idcode(cls, id_code, raise_if_none=True):
        truck = cls.objects(id_code=id_code).first()
        if not truck and raise_if_none:
            raise NameError('Camion codigo "{}" no encontrado.'.format(id_code))
        return truck

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]

class Project(db.Document):
    """
    Project class
    """
    meta = {'collection': 'projects'}
    name = db.StringField(required=True, unique=True, max_length=50)
    description = db.StringField(max_length=150)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.now())

    @classmethod
    def add(cls, name, description=None):
        return cls(name=name, description=description).save()

    @classmethod
    def find_by_name(cls, name, raise_if_none=True):
        project = cls.objects(name=name).first()
        if not project and raise_if_none:
            raise NameError('Obra "{}" no encontrada.'.format(name))
        return project

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]

class Material(db.Document):
    """
    Material class
    """
    meta = {'collection': 'materials'}
    name = db.StringField(required=True, unique=True, max_length=50)
    description = db.StringField(max_length=150)

    @classmethod
    def add(cls, name, description=None):
        return cls(name=name, description=description).save()

    @classmethod
    def find_by_name(cls, name, raise_if_none=True):
        material = cls.objects(name=name).first()
        if not material and raise_if_none:
            raise NameError('Material "{}" no encontrado.'.format(name))
        return material

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]

class Origin(db.Document):
    """
    Origin class
    """
    meta = {'collection': 'origins'}
    name = db.StringField(required=True, unique=True, max_length=50)
    location = db.StringField(unique=True, sparse=True, max_length=150)
    description = db.StringField(max_length=150)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.now())

    @classmethod
    def add(cls, name, location=None, description=None):
        return cls(name=name, location=location, description=description).save()

    @classmethod
    def find_by_name(cls, name, raise_if_none=True):
        origin = cls.objects(name=name).first()
        if not origin and raise_if_none:
            raise NameError('Origen "{}" no encontrado.'.format(name))
        return origin

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]

class Destination(db.Document):
    """
    Destination class
    """
    meta = {'collection': 'destinations'}
    name = db.StringField(required=True, unique=True, max_length=50)
    location = db.StringField(unique=True, sparse=True, max_length=150)
    description = db.StringField(max_length=150)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.now())

    @classmethod
    def add(cls, name, location=None, description=None):
        return cls(name=name, location=location, description=description).save()

    @classmethod
    def find_by_name(cls, name, raise_if_none=True):
        destination = cls.objects(name=name).first()
        if not destination and raise_if_none:
            raise NameError('Destino "{}" no encontrado.'.format(name))
        return destination

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]