from cursa_acarreo import db
import datetime


"""
Validation functions
"""


def _validate_no_duplicates(lst):  # General purpose validation
    """
    Validate there are no duplicates values in the field
    :param list: list to be validated
    :return: mongoeninge.ValidationError if there are duplicate values
    """
    if True in [lst.count(i) > 1 for i in lst]:
        raise db.ValidationError('Duplicate values found. Field cannot have duplicates')


def _validate_no_duplicate_objects(list):
    """
    Validate that there are no duplicates objects in ListField
    :param list: list of ListField
    :return: mongonengine.ValidationError if there are duplicate objects in the list
    """
    list_of_object_by_id = [i.id for i in list]
    try:
        _validate_no_duplicates(list_of_object_by_id)
    except db.ValidationError:
        raise db.ValidationError('Duplicate objects in ListField Found. Cannot have duplicates.')


"""
Model classes
"""


class Driver(db.Document):
    """
    Driver model
    """
    meta = {'collection': 'drivers'}

    name = db.StringField(required=True, max_length=50)
    last_name = db.StringField(unique_with='name', required=True, max_length=50)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.utcnow)

    @classmethod
    def add(cls, name, last_name):
        return cls(name=name.upper(), last_name=last_name.upper()).save()

    @classmethod
    def find_by_full_name(cls, name, last_name, raise_if_none=True):
        driver = cls.objects(name__iexact=name, last_name__iexact=last_name).first()
        if not driver and raise_if_none:
            raise NameError('Conductor "{}" no encontrado.'.format(name + " " + last_name))
        return driver

    @classmethod
    def get_all(cls):
        return [{'name': i.name, 'last_name': i.last_name} for i in cls.objects]

class Supplier(db.Document):
    """
    Supplier model
    """
    meta = {'collection': 'suppliers'}
    name = db.StringField(required=True, unique=True, sparse=True, max_length=50)

    @classmethod
    def add(cls, name):
        return cls(name=name.upper()).save()

    @classmethod
    def find_by_name(cls, name, raise_if_none=True):
        supplier = cls.objects(name__iexact=name).first()
        if not supplier and raise_if_none:
            raise NameError('"{}" no encontrado.'.format(name.upper()))
        return supplier

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]


class Customer(db.Document):
    """
    Customer model
    """
    meta = {'collection': 'customers'}
    name = db.StringField(required=True, unique=True, sparse=True, max_length=50)

    @classmethod
    def add(cls, name):
        return cls(name=name.upper()).save()

    @classmethod
    def find_by_name(cls, name, raise_if_none=True):
        customer = cls.objects(name__iexact=name).first()
        if not customer and raise_if_none:
            raise NameError('"{}" no encontrado.'.format(name))
        return customer

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]


class Truck(db.Document):
    """
    Truck model
    """
    meta = {'collection': 'trucks'}
    id_code = db.StringField(required=True, unique=True, max_length=50)
    brand = db.StringField(max_length=50)
    color = db.StringField(max_length=50)
    serial_number = db.StringField(required=True, unique=True, sparse=True, max_length=50)  # mark as required???
    plate = db.StringField(required=False, unique=True, sparse=True, max_length=50)  # mark as required???
    capacity = db.IntField(required=False, min_value=0)
    driver = db.ReferenceField(Driver, dbref=True, reverse_delete_rule=db.NULLIFY)
    owner = db.ReferenceField(Supplier, dbref=True, reverse_delete_rule=db.NULLIFY)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.utcnow)
    is_active = db.BooleanField(default=True)

    def json(self):
        skip_items = []
        d_json = dict()
        for i in self:
            if i not in skip_items:
                if i == 'driver' and self[i]:
                    d_json[i] = {'name': self[i].name, 'last_name': self[i].last_name}
                elif i == 'owner' and self[i]:
                    d_json[i] = self[i].name
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

    # def _get_driver(self, name, last_name):
    #     driver = Driver.find_by_full_name(name, last_name)
    #     if not driver:
    #         raise db.ValidationError('El chofer "{}", que intenta agregar no esta dado de alta en el '
    #                                  'sistema'.format(name + " " + last_name))
    #     return driver

    def set_driver(self, name, last_name):
        driver = Driver.find_by_full_name(name, last_name)
        self.driver = driver
        self.save_to_db()

    def set_owner(self, name):
        supplier = Supplier.find_by_name(name, False)
        if supplier:
            self.owner = supplier
            self.save_to_db()
        else:
            raise NameError('Proveedor "{}" no encontrado en sistema. Favor de agregarlo primero.'.format(name))

    @classmethod
    def add(cls, id_code, serial_number, brand=None, color=None, plate=None, driver_name=None, capacity=None,
            owner_name=None, is_active=None):
        """

        :param id_code:
        :param serial_number:
        :param brand:
        :param color:
        :param plate:
        :param driver_name:
        :param capacity:
        :param owner_name: must be a tuple ('first name', 'last name')
        :param is_active:
        :return:
        """
        if driver_name:
            if not isinstance(driver_name, tuple):
                raise TypeError('Driver name must be a tuple with format ("name","last_name")')
            driver = Driver.find_by_full_name(driver_name[0], driver_name[1])
        else:
            driver = driver_name
        if owner_name:
            owner = Supplier.find_by_name(owner_name)
        else:
            owner = owner_name
        params = {
            'id_code': id_code.upper(),
            'serial_number': serial_number.upper(),
            'brand': brand.upper() if brand else brand,
            'color': color.upper() if color else color,
            'plate': plate.upper() if plate else plate,
            'capacity': capacity,
            'driver': driver,
            'owner': owner,
            'is_active': is_active
        }
        return cls(**params).save()

    @classmethod
    def find_by_idcode(cls, id_code, raise_if_none=True):
        truck = cls.objects(id_code__iexact=id_code).first()
        if not truck and raise_if_none:
            raise NameError('Camion codigo "{}" no encontrado.'.format(id_code))
        return truck

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
    is_active = db.BooleanField(default=True)

    @classmethod
    def add(cls, name, description=None, is_active=None):
        return cls(name=name.upper(), description=description, is_active=is_active).save()

    @classmethod
    def delete_by_name(cls, name):
        material = cls.find_by_name(name, False)
        if material:
            material.delete()
        else:
            raise NameError('Material "{}" no encontrado.'.format(name.upper()))

    @classmethod
    def find_by_name(cls, name, raise_if_none=True):
        material = cls.objects(name__iexact=name).first()
        if not material and raise_if_none:
            raise NameError('Material "{}" no encontrado.'.format(name))
        return material

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]


class Project(db.Document):
    """
    Project class
    """
    meta = {'collection': 'projects'}
    name = db.StringField(required=True, unique=True, max_length=50)
    location = db.StringField(max_length=150)
    description = db.StringField(max_length=150)
    customer = db.ReferenceField(Customer, dbref=True, reverse_delete_rule=db.NULLIFY)
    resident = db.StringField(max_length=50)
    materials_required = db.ListField(db.ReferenceField(Material, dbref=True, reverse_delete_rule=db.PULL),
                                      validation=_validate_no_duplicate_objects)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.utcnow)
    is_active = db.BooleanField(default=True)

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

    def add_materials(self, material_name):
        if not isinstance(material_name, list):
            material_name = [material_name]
        for i in material_name:
            try:
                material = Material.find_by_name(i)
                self.materials_required.append(material)
            except NameError:
                self.reload()
                raise NameError('Material "{}" no encontrado. Ningún material fue agregado. '
                                'Favor de agregar a lista de materiales primero. '.format(i.upper()))
        self.save_to_db()

    def remove_material(self, material_name):
        if material_name in [i.name for i in self.materials_required]:
            material = Material.find_by_name(material_name)
            self.materials_required.remove(material)
            self.save_to_db()
        else:
            raise NameError('Material "{}" no encontrado en lista de materiales de obra. '
                            'Ningun material fue removido'.format(material_name))

    def get_list_of_materials(self):
        return [i.name for i in self.materials_required]

    def set_customer(self, name):
        customer = Customer.find_by_name(name, False)
        if customer:
            self.customer = customer
            self.save_to_db()
        else:
            raise NameError('Cliente "{}" no encontrado en sistema. Favor de agregarlo primero.'.format(name))

    @classmethod
    def add(cls, name, description=None, location=None, customer_name=None, resident=None, is_active=None):
        if customer_name:
            customer = Customer.find_by_name(customer_name)
        else:
            customer = customer_name
        params = {
            'name': name.upper(),
            'description': description.upper() if description else description,
            'location': location.upper() if location else location,
            'customer': customer,
            'resident': resident.upper if resident else resident,
            'is_active': is_active
        }
        return cls(**params).save()

    @classmethod
    def find_by_name(cls, name, raise_if_none=True):
        project = cls.objects(name__iexact=name).first()
        if not project and raise_if_none:
            raise NameError('Obra "{}" no encontrada.'.format(name))
        return project

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]


class MaterialBank(db.Document):
    """
    MaterialBank class
    """
    meta = {'collection': 'material_banks'}
    name = db.StringField(required=True, unique=True, max_length=50)
    location = db.StringField(unique=True, sparse=True, max_length=150)
    description = db.StringField(max_length=150)
    owner = db.ReferenceField(Supplier, dbref=True, reverse_delete_rule=db.NULLIFY)
    materials_available = db.ListField(db.ReferenceField(Material, dbref=True, reverse_delete_rule=db.PULL),
                                      validation=_validate_no_duplicate_objects)
    royalty = db.DecimalField(min_value=0, precision=2, default=0)
    date_added = db.DateTimeField(required=True, default=datetime.datetime.utcnow)
    is_active = db.BooleanField(default=True)

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

    def set_owner(self, name):
        supplier = Supplier.find_by_name(name, False)
        if supplier:
            self.owner = supplier
            self.save_to_db()
        else:
            raise NameError('Proveedor "{}" no encontrado en sistema. Favor de agregarlo primero.'.format(name))

    def add_materials(self, material_name):
        if not isinstance(material_name, list):
            material_name = [material_name]
        for i in material_name:
            try:
                material = Material.find_by_name(i)
                self.materials_available.append(material)
            except NameError:
                self.reload()
                raise NameError('Material "{}" no encontrado. Ningún material fue agregado. '
                                'Favor de agregar a lista de materiales primero. '.format(i.upper()))
        self.save_to_db()

    def remove_material(self, material_name):
        if material_name.upper() in [i.name for i in self.materials_available]:
            material = Material.find_by_name(material_name)
            self.materials_required.remove(material)
            self.save_to_db()

        else:
            raise NameError('Material "{}" no encontrado en lista de materiales de obra. '
                            'Ningun material fue removido'.format(material_name.upper()))

    def get_list_of_materials(self):
        return [i.name for i in self.materials_available]

    @classmethod
    def add(cls, name, location=None, description=None, owner_name=None, royalty=None, is_active=None):
        if owner_name:
            owner = Supplier.find_by_name(owner_name)
        else:
            owner = owner_name
        params = {
            'name': name.upper(),
            'location': location.upper() if location else location,
            'description': description.upper() if description else description,
            'owner': owner,
            'royalty': royalty,
            'is_active':is_active
        }
        return cls(**params).save()

    @classmethod
    def find_by_name(cls, name, raise_if_none=True):
        origin = cls.objects(name__iexact=name).first()
        if not origin and raise_if_none:
            raise NameError('Banco: "{}" no encontrado.'.format(name.upper()))
        return origin

    @classmethod
    def get_list_by(cls, param):
        return [t[param] for t in cls.objects]