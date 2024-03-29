from cursa_acarreo import db
from cursa_acarreo.models.general import Truck, Project, Material, MaterialBank, Driver
from cursa_acarreo.models.user import User
import datetime
from mongoengine import queryset_manager

from ..utils import utils

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


# def validate_driver_options(value):
#     if not Driver.find_by_full_name(value, raise_if_none=False):
#         raise db.ValidationError('Chofer {} no encontrado en lista de choferes registrados.'.format(value))

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
TRIP_TYPES_LIST = ('internal', 'public')

STATUS_TRANSLATION = {'in_progress': 'En Proceso', 'complete': 'Completo', 'canceled': 'Cancelado'}
TYPE_TRANSLATION = {'internal': 'Interno', 'public': 'Público'}

# TODO:
# Add validation for either amount or weight_in_kg considering 'is_trip_by_weight'

MAX_WEIGHT_IN_KG = 70000  #


class Trip(db.Document, Base):
    """
    Trip model
    """
    meta = {'collection': 'trips'}
    trip_id = db.SequenceField(primary_key=True)
    truck = db.StringField(required=False, validation=validate_truck_options)
    driver = db.StringField(required=False)
    material = db.StringField(required=True, validation=validate_material_options)
    amount = db.IntField(required=False, min_value=0)  # In mts3
    is_trip_by_weight = db.BooleanField(default=False)
    weight_in_kg = db.IntField(required=False, min_value=0, max_value=MAX_WEIGHT_IN_KG)
    origin = db.StringField(required=True, validation=validate_location_options)
    destination = db.StringField(required=False, validation=validate_location_options)
    distance = db.IntField(required=False, min_value=0)  # In kms
    client = db.StringField(required=False)
    sender_user = db.StringField(required=True, validation=validate_user_options)
    sender_comment = db.StringField(required=False, max_length=100)
    sent_datetime = db.DateTimeField(required=True, default=datetime.datetime.utcnow)
    finalizer_user = db.StringField(validation=validate_user_options)
    finalizer_comment = db.StringField(required=False, max_length=100)
    finalized_datetime = db.DateTimeField()
    status = db.StringField(required=False, choices=STATUS_LIST)
    is_return = db.BooleanField(default=False)
    type = db.StringField(required=True, choices=TRIP_TYPES_LIST)
    is_deleted = db.BooleanField(default=False)

    def json(self):
        trip_dict = dict()
        for i in self:
            if (i in ['sender_comment', 'finalizer_comment', 'client', 'destination', 'truck', 'driver',
                      'finalizer_user', 'distance']) \
                    and (self[i] is None):  # (i == 'sender_comment' or i == 'finalizer_comment')
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
            return self.save(validate=validation)
        except Exception as e:
            self.reload()
            raise e

    def finalize(self, username, status, distance, finalizer_comment=None):
        """
        Move trip to complete or canceled.
        :param username: username of user doing the operation
        :param status: "complete" or "canceled"
        :param finalizer_comment: optional comment
        :return:
        """
        self.status = status
        self.finalizer_user = username
        self.distance = distance if distance else None
        self.finalizer_comment = finalizer_comment if finalizer_comment else None
        self.finalized_datetime = datetime.datetime.utcnow()
        self.save_to_db(
            validation=False)  # This is a temporary solution, instead code logic to execute validate_x_options

    def delete(self):
        self.is_deleted = True
        self.save_to_db(validation=False)

    @classmethod
    def create(cls, truck_id, material_name, origin_name, sender_username, type,
               status='in_progress', destination_name=None, client_name=None, sender_comment=None, amount=None,
               is_trip_by_weight=False, weight_in_kg=None, is_return=None):

        truck = Truck.find_by_idcode(truck_id, raise_if_none=False)

        params = {
            'truck': truck_id.upper() if truck_id else None,
            'driver': truck.driver.get_full_name()
            if Truck.find_by_idcode(truck_id, False) and truck.driver else None,
            'material': material_name.upper(),
            'origin': origin_name.upper(),
            'destination': destination_name.upper() if destination_name else None,
            'client': client_name.upper() if client_name else None,
            'sender_user': sender_username,
            'sender_comment': sender_comment if sender_comment else None,
            'amount': amount if amount is not None and amount != '' and not is_trip_by_weight else
                        (truck.capacity if not is_trip_by_weight else None),
            'is_trip_by_weight': is_trip_by_weight,
            'weight_in_kg': weight_in_kg if weight_in_kg is not None and weight_in_kg != '' else None,
            'status': status,
            'is_return': is_return,
            'type': type
        }

        # Logic requires approval from Cursa. Case when Destination is a MaterialBank or bank to bank
        # if type == 'internal' and destination_name:
        #     customer = Project.find_by_name(destination_name).customer
        #     params['client'] = customer.name if customer else None
        # elif type == 'public' and client_name:
        #     params['client'] = client_name
        # else:
        #     params['client'] = None

        return cls(**params).save()

    @queryset_manager
    def objects_no_deleted(cls, queryset):
        # return queryset.filter(trip_id__gte=21000, is_deleted__ne=True) # Temporary p
        return queryset.filter(is_deleted__ne=True)

    @classmethod
    def find_by_tripid(cls, trip_id, raise_if_none=True):
        trip = cls.objects_no_deleted(trip_id__iexact=trip_id).first()
        if not trip and raise_if_none:
            raise NameError('Viaje "#{}" no existe'.format(trip_id))
        return trip

    @classmethod
    def get_by_status(cls, status: list):
        return [trip.json() for trip in cls.objects_no_deleted(status__in=status)]

    @classmethod
    def get_all(cls):
        return [trip.json() for trip in cls.objects_no_deleted()]

    @classmethod
    def get_complete_and_cancelled(cls):
        return [trip.json() for trip in cls.objects_no_deleted(status__in=['complete', 'canceled']).order_by('-_id')]

    @classmethod
    def get_formatted_trips(cls, status=['complete', 'canceled'], purpose='table'):
        #     [{trip_id:'', ...},{}]
        trips = cls.objects_no_deleted(status__in=status).order_by('-_id')
        formatted_list = []
        for trip in trips:
            if purpose == 'table':
                formatted_list.append({
                    'trip_id': trip.trip_id,
                    'type': TYPE_TRANSLATION[trip.type] if trip.type else 'Interno',
                    'status': STATUS_TRANSLATION[trip.status],
                    'truck': trip.truck if trip.truck else '',
                    'driver': trip.driver if trip.driver else '',
                    'material': trip.material,
                    'amount': trip.amount if trip.amount is not None else '',
                    'weight_in_tons': trip.weight_in_kg / 1000 if trip.weight_in_kg is not None and trip.is_trip_by_weight else '',
                    'origin': trip.origin,
                    'destination': trip.destination if trip.destination else '',
                    'distance': trip.distance if trip.distance is not None else '',
                    'client': trip.client if trip.client else '',
                    'sender_user': trip.sender_user,
                    'sent_datetime': utils.formatdate_mx(trip.sent_datetime),
                    'sender_comment': trip.sender_comment if trip.sender_comment else '',
                    'finalizer_user': trip.finalizer_user if trip.finalizer_user else '',
                    'finalized_datetime': utils.formatdate_mx(trip.finalized_datetime),
                    'finalizer_comment': trip.finalizer_comment if trip.finalizer_comment else ''
                })
            elif purpose == 'csv':
                formatted_list.append({
                    '#': trip.trip_id,
                    'Tipo': TYPE_TRANSLATION[trip.type] if trip.type else 'Interno',
                    'Estado': STATUS_TRANSLATION[trip.status],
                    'Camión': trip.truck if trip.truck else '',
                    'Chofer': trip.driver if trip.driver else '',
                    'Material': trip.material,
                    'mts3': trip.amount if trip.amount is not None else '',
                    'Peso(t)': trip.weight_in_kg / 1000 if trip.weight_in_kg is not None and trip.is_trip_by_weight else '',
                    'Origen': trip.origin,
                    'Destino': trip.destination if trip.destination else '',
                    'Kms': trip.distance if trip.distance is not None else '',
                    'Cliente': trip.client if trip.client else '',
                    'Envió': trip.sender_user,
                    'Fecha/Hora Envío': utils.formatdate_mx(trip.sent_datetime),
                    'Comentario Envío': trip.sender_comment if trip.sender_comment else '',
                    'Finalizó': trip.finalizer_user if trip.finalizer_user else '',
                    'Fecha/Hora Finalizado': utils.formatdate_mx(trip.finalized_datetime),
                    'Comentario Recibo': trip.finalizer_comment if trip.finalizer_comment else ''
                })
        return formatted_list

    @classmethod
    def get_distinct_values(cls, field):
        return cls.objects_no_deleted().distinct(field)

    @classmethod
    def get_trucks_in_trip(cls):
        return list(dict.fromkeys([t.truck for t in cls.objects_no_deleted(status='in_progress')]))
