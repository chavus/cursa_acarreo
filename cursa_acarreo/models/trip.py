from cursa_acarreo import db
from cursa_acarreo.models.general import Truck, Project, Material, MaterialBank
from cursa_acarreo.models.user import User
import datetime

"""
Base Class
"""


class Base:
    @classmethod
    def update_field(cls, field, old_value, new_value):
        find_query = {field: old_value}
        update_query = {field: new_value}
        cls.objects(**find_query).update(**update_query)


"""
Validation Functions
"""


def validate_truck_options(value):
    if not Truck.find_by_idcode(value, raise_if_none=False):
        raise db.ValidationError('Camión {} no encontrado en lista de camiones.'.format(value))


def validate_material_options(value):
    if not Material.find_by_name(value, raise_if_none=False):
        raise db.ValidationError('Material {} no encontrado en lista de materiales.'.format(value))


def validate_location_options(value):
    if not (MaterialBank.find_by_name(value, raise_if_none=False) or Project.find_by_name(value, raise_if_none=False)):
        raise db.ValidationError('Ubicación {} no encontrado en lista de bancos ni obras.'.format(value))


def validate_user_options(value):
    if not User.find_by_username(value, raise_if_none=False):
        raise db.ValidationError('Usuario {} no encontrado en lista de usuarios.'.format(value))


"""
Model classes
"""


STATUS_LIST = ('in_progress', 'complete', 'canceled')
class Trip(db.Document, Base):
    """
    Trip model
    """
    meta = {'collection': 'trips'}
    trip_id = db.SequenceField(primary_key=True)
    truck = db.StringField(required=True, validation=validate_truck_options)
    material = db.StringField(required=True, validation=validate_material_options)
    amount = db.IntField(required=True, min_value=0)
    origin = db.StringField(required=True, validation=validate_location_options)
    destination = db.StringField(required=True, validation=validate_location_options)
    sender_user = db.StringField(required=True, validation=validate_user_options)
    sender_comment = db.StringField(required=False, max_length=100)
    sent_datetime = db.DateTimeField(required=True, default=datetime.datetime.utcnow)
    finalizer_user = db.StringField(validation=validate_user_options)
    finalizer_comment = db.StringField(required=False, max_length=100)
    finalized_datetime = db.DateTimeField()
    status = db.StringField(required=False, choices=STATUS_LIST)
    is_return = db.BooleanField(defaul=False)

    def json(self):
        trip_dict = dict()
        for i in self:
            if (i == 'sender_comment' or i == 'finalizer_comment') and (self[i] is None):
                trip_dict[i] = ''
            else:
                trip_dict[i] = self[i]
        return trip_dict

    def save_to_db(self, validation=True):
        """
        Try to save instance. If there is an error, it reload info from DB to discard changes.
        :param self:
        :return:
        """
        try:
            self.save(validate=validation)
        except Exception as e:
            self.reload()
            raise e

    def finalize(self, username, status, finalizer_comment=None):
        """
        Move trip to complete or canceled.
        :param username: username of user doing the operation
        :param status: "complete" or "canceled"
        :param finalizer_comment: optional comment
        :return:
        """
        self.status = status
        self.finalizer_user = username
        self.finalizer_comment = finalizer_comment
        self.finalized_datetime = datetime.datetime.utcnow()
        self.save_to_db(validation=False)  # This is a temporary solution, instead code logic to execute validate_x_options

    @classmethod
    def create(cls, truck_id, material_name, origin_name, destination_name, sender_username, sender_comment=None,
               amount=None, is_return=None):
        params = {
            'truck': truck_id.upper(),
            'material': material_name.upper(),
            'origin': origin_name.upper(),
            'destination': destination_name.upper(),
            'sender_user': sender_username,
            'sender_comment': sender_comment,
            'amount': amount if amount else Truck.find_by_idcode(truck_id).capacity,
            'status': 'in_progress',
            'is_return': is_return
        }
        return cls(**params).save()

    @classmethod
    def find_by_tripid(cls, trip_id, raise_if_none=True):
        trip = cls.objects(trip_id__iexact=trip_id).first()
        if not trip and raise_if_none:
            raise NameError('Viaje "#{}" no existe'.format(trip_id))
        return trip

    @classmethod
    def get_all(cls):
        return [trip.json() for trip in cls.objects]

    @classmethod
    def get_trucks_in_trip(cls):
        return list(dict.fromkeys([t.truck for t in cls.objects(status='in_progress')]))



