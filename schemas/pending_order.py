from mongoengine import Document, ReferenceField, IntField, DateTimeField, StringField

from schemas.stock import Stock
from schemas.user import User

class PendingOrder(Document):
    stock_id=StringField()
    user_id=StringField()
    lower_bound=IntField()
    upper_bound=IntField()
    total=IntField()
    type=StringField()

