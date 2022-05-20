import time
import schedule
from routes.stock import BuyHandler, SellHandler
from schemas.pending_order import PendingOrder
from mongoengine import *

connect(host="localhost")
def retry():
    print("Scheduler STARTED")
    pending_orders = PendingOrder.objects()
    for order in pending_orders:
        if order.type == "buy":
            buy = BuyHandler()
            status = buy.handle(order)
        elif order.type == "sell":
            sell = SellHandler()
            status = sell.handle(order)

        if status == "ok":
            PendingOrder.objects(id=order.id).delete()

# async def run_job():
#     await schedule.every(1).minutes.do(retry)

schedule.every(1).minutes.do(retry)

while True:
   schedule.run_pending()
   time.sleep(1)