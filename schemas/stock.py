from mongoengine import Document, EmbeddedDocument, StringField, IntField, ListField, EmbeddedDocumentField,DateTimeField

class History(EmbeddedDocument):
    timestamp=DateTimeField()
    price=IntField()

class Stock(Document):
    stock_id=StringField()
    name=StringField()
    price=IntField()
    availability=IntField()
    updated_at=StringField()
    history=ListField(EmbeddedDocumentField(History))
    max_price_hour=IntField(default=0)
    min_price_hour=IntField(default=0)
    max_price_day=IntField(default=0)
    min_price_day=IntField(default=0)

 
