from cursa_acarreo import db
from cursa_acarreo.models.general import Driver, Truck, Project, Material, Origin
from cursa_acarreo.models.user import User
import datetime


STATUS_LIST = ('in_progress', 'complete', 'canceled')
class Trip(db.Document):
    """
    Trip model
    """
    meta = {'collection': 'trips'}
    trip_id = db.SequenceField(primary_key=True)
    truck = db.ReferenceField(Truck, required=True)
    material = db.ReferenceField(Material, required=True)
    amount = db.IntField(min_value=0, required=True)
    project = db.ReferenceField(Project, required=True)
    origin = db.ReferenceField(Origin, required=True)
    # destination = db.ReferenceField(Destination, required=True)
    sender_user = db.ReferenceField(User, required=True)
    sent_datetime = db.DateTimeField(required=True)
    finalizer_user = db.ReferenceField(User)
    finalized_datetime = db.DateTimeField()
    status = db.StringField(required=True, choices=STATUS_LIST)

    def json(self):
        trip_dict = dict()
        for i in self:
            if i == 'truck':
                trip_dict[i] = self[i].id_code
            elif i in ['sender_user', 'finalizer_user'] and self[i]:
                trip_dict[i] = self[i].username
            elif i in ['material', 'project', 'origin']:
                trip_dict[i] = self[i].name
            else:
                trip_dict[i] = self[i]

        return trip_dict

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

    def finalize(self, username, status):
        """
        Move trip to complete or canceled.
        :param username: username of user doing the operation
        :param status: "complete" or "canceled"
        :return:
        """
        self.status = status
        self.finalizer_user = User.find_by_username(username)
        self.finalized_datetime = datetime.datetime.utcnow()
        self.save_to_db()

    @classmethod
    def create(cls, truck_id, material_name, project_name, origin_name, sender_username, amount=None,
               sent_datetime=datetime.datetime.utcnow()):
        params = {
            'truck': Truck.find_by_idcode(truck_id),
            'material': Material.find_by_name(material_name),
            'project': Project.find_by_name(project_name),
            'origin': Origin.find_by_name(origin_name),
            'sender_user': User.find_by_username(sender_username),
            'sent_datetime': sent_datetime,
            'amount': amount if amount else Truck.find_by_idcode(truck_id).capacity,
            'status': 'in_progress'
        }
        return cls(**params).save()

    @classmethod
    def find_by_tripid(cls, trip_id, raise_if_none=True):
        trip = cls.objects(trip_id=trip_id).first()
        if not trip and raise_if_none:
            raise NameError('Viaje "#{}" no existe'.format(trip_id))
        return trip

    @classmethod
    def get_all(cls):
        return [trip.json() for trip in cls.objects]


