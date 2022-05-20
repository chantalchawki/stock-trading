import json
import paho.mqtt.client as mqtt
from schemas.stock import History, Stock
from mongoengine import *
from datetime import datetime

connect(host="localhost")

def on_message(client, userdata, msg):
    print("ON MESSAGE")
    entry = json.loads(msg.payload)

    try:
        existing_stock = Stock.objects(stock_id=entry["stock_id"]).only('updated_at')
        print(existing_stock[0].updated_at)

        history = History(timestamp=entry["timestamp"], price=entry["price"])    
        Stock.objects(stock_id=entry["stock_id"]).update_one(push__history=history)

        updated_at = datetime.strptime(existing_stock[0].updated_at, '%Y-%m-%d %H:%M:%S.%f')
        timestamp_date = datetime.strptime(entry["timestamp"], '%Y-%m-%d %H:%M:%S.%f')
        
        if updated_at < timestamp_date:
            Stock.objects(stock_id=entry["stock_id"]).update_one(set__price=entry["price"], set__availability=entry["availability"], set__updated_at=entry["timestamp"])

    except:
        history = [History(timestamp= entry["timestamp"], price=entry["price"])]
        new_stock = Stock(stock_id=entry["stock_id"], name=entry["name"], price=entry["price"], availability=entry["availability"], updated_at=entry["timestamp"], history=history)
        new_stock.save()
       
def on_log(client, userdata, level, buf):
    print("log: ",buf)

client = mqtt.Client()
client.on_message = on_message
client.on_log=on_log

client.connect("localhost", 1883)
client.subscribe("thndr-trading")

client.loop_forever()