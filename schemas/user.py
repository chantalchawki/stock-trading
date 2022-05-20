from mongoengine import Document, StringField, IntField, ListField, DateTimeField, EmbeddedDocumentField, EmbeddedDocument

class Order(EmbeddedDocument):
    price=IntField()
    number_of_stocks=IntField()
    stock_id=StringField()
    created_at=DateTimeField()
    type=StringField()

class UserStock(EmbeddedDocument):
    stock_id=StringField()
    number=IntField(default=0)

class User(Document):
    name=StringField()
    fund=IntField()
    orders=ListField(EmbeddedDocumentField(Order))
    stocks=ListField(EmbeddedDocumentField(UserStock))