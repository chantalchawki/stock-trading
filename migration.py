from mongoengine import *
from schemas.user import User

connect(host='localhost')

user1 = User(name="Mahmoud", fund=5000)
user1.save()

user2 = User(name="Abdo", fund=2000)
user2.save()