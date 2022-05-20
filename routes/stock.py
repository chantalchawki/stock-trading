from abc import abstractmethod
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from schemas.pending_order import PendingOrder
from schemas.stock import Stock
from schemas.user import Order, User, UserStock
from datetime import datetime, timedelta


stock = APIRouter()

class FindStockRequest(BaseModel):
    stock_id: str

class FindStockResponse(BaseModel):
    name: str
    price: int
    availability: int
    max_price_day: int
    max_price_hour: int
    min_price_day: int
    min_price_hour: int

class OrderStockRequest(BaseModel):
    user_id: str
    stock_id: str
    total: int
    lower_bound: int
    upper_bound: int

@stock.post('/stock', response_model=FindStockResponse)
async def find_stock(body: FindStockRequest):
    try:
        pipeline = [
            { '$match': {'stock_id': body.stock_id} },
            { '$project': {
                'hour': {
                    '$filter': {
                        'input': '$history', 
                        'as': 'item', 
                        'cond': {
                            '$gte': ['$$item.timestamp', datetime.utcnow() - timedelta(hours=4)]
                        }
                    }
                }, 
                'day': {
                    '$filter': {
                        'input': '$history', 
                        'as': 'item', 
                        'cond': {
                            '$gte': ['$$item.timestamp', datetime.utcnow() - timedelta(hours=24)]
                        }
                    }
                }
            }
            },
            { '$project': {
                'maxPriceHour': { '$max': '$hour.price' }, 
                'minPriceHour': { '$min': '$hour.price' }, 
                'maxPriceDay': { '$max': '$day.price' }, 
                'minPriceDay': { '$min': '$day.price' }
            }
            }]

        data = Stock.objects().aggregate(pipeline).next()
        res = Stock.objects.get(stock_id=body.stock_id)
        if data["maxPriceHour"] == None:
            return FindStockResponse(name=res.name, price=res.price, availability=res.availability, max_price_day=res.max_price_day, max_price_hour=res.max_price_hour, min_price_day=res.min_price_day, min_price_hour=res.min_price_hour)

        else:
            Stock.objects(stock_id=body.stock_id).update_one(set__max_price_hour=data["maxPriceHour"], set__max_price_day=data["maxPriceDay"], set__min_price_hour=data["minPriceHour"], set__min_price_day=data["minPriceDay"])
            return FindStockResponse(name=res.name, price=res.price, availability=res.availability, max_price_day=data["maxPriceDay"], max_price_hour=data["maxPriceHour"], min_price_day=data["minPriceDay"], min_price_hour=data["minPriceHour"])

    except:
        return JSONResponse(status_code=404, content={"message": "stock not found"})

@stock.post('/sell', status_code=202)
async def sell_stock(body: OrderStockRequest):
    sell = SellHandler()
    status = sell.handle(body)
    if status == False:
        pending_order = PendingOrder(user_id=body.user_id, stock_id=body.stock_id, lower_bound=body.lower_bound, upper_bound=body.upper_bound, type="sell", total=body.total)
        pending_order.save()
        return "pending"
    else: 
        return status

@stock.post('/buy', status_code=202)
async def buy_stock(body: OrderStockRequest):
    buy = BuyHandler()
    status = buy.handle(body)
    if status == False:
        pending_order = PendingOrder(user_id=body.user_id, stock_id=body.stock_id, lower_bound=body.lower_bound, upper_bound=body.upper_bound, type="buy", total=body.total)
        pending_order.save()
        return "pending"
    else: 
        return status

 
class OrderHandler():

    @abstractmethod
    def can_proceed(self, user, stock, body):
        pass

    @abstractmethod
    def update_fund(self, user, stock, body):
        pass

    @abstractmethod
    def update_stock_number(self, user_stock, body):
        pass

    def has_enough_stocks(self, body, user_stock):
        return True
    
    def add_new_stock(self, body, order, fund):
        pass

    @abstractmethod
    def type(self):
        pass

    def handle(self, body):
        user = User.objects.get(id=body.user_id)
        stock = Stock.objects.get(stock_id=body.stock_id)
        if self.can_proceed(user, stock, body):
            fund = self.update_fund(user, stock, body)
            found = False
            for user_stock in user.stocks:
                if body.stock_id == user_stock.stock_id:
                    if self.has_enough_stocks(body, user_stock) == False:
                        break
                    number = self.update_stock_number(user_stock, body)
                    User.objects(id=body.user_id, stocks__stock_id=body.stock_id).update_one(set__stocks__S__number=number)
                    found = True
                    break
                
            order = Order(price=stock.price, number_of_stocks=body.total, stock_id=body.stock_id, created_at=datetime.utcnow(), type=self.type())

            if found:
                User.objects(id=body.user_id).update_one(push__orders=order, set__fund=fund)
            else:
                self.add_new_stock(body, order, fund)

            return "ok"
        return False


class BuyHandler(OrderHandler): 
    def can_proceed(self, user, stock, body):
        return user.fund >= stock.price * body.total and body.lower_bound <= stock.price <= body.upper_bound

    def update_fund(self, user, stock, body):
        return user.fund - (stock.price * body.total)

    def update_stock_number(self, user_stock, body):
        return user_stock.number + body.total
    
    def add_new_stock(self, body, order, fund):
        stock = UserStock(stock_id=body.stock_id, number=body.total)
        User.objects(id=body.user_id).update_one(push__orders=order, push__stocks=stock, set__fund=fund)
        return "ok"
    
    def type(self):
        return "buy"

class SellHandler(OrderHandler):
    def can_proceed(self, user, stock, body):
        return body.lower_bound <= stock.price <= body.upper_bound

    def update_fund(self, user, stock, body):
        return user.fund + (stock.price * body.total)

    def update_stock_number(self, user_stock, body):
        return user_stock.number - body.total

    def has_enough_stocks(self, body, user_stock):
        return user_stock.number >= body.total
    
    def add_new_stock(self, body, order, fund):
        return "error"

    def type(self):
        return "sell"