from datetime import datetime
import json
from fastapi import APIRouter
from pydantic import BaseModel
from schemas.user import Order, User
from typing import List

user = APIRouter()
class FundUserRequest(BaseModel):
    user_id: str
    amount: int

class FindUserRequest(BaseModel):
    user_id: str

class Order(BaseModel):
    price: int
    number_of_stocks: int
    stock_id: str
    created_at: datetime
    type: str

class Stock(BaseModel):
    stock_id: str
    number: int

class FindUserResponse(BaseModel):
    name: str
    fund: int
    orders: List[Order]
    stocks: List[Stock]

@user.post('/user', response_model=FindUserResponse)
async def find_user(body: FindUserRequest):
    res = User.objects.get(id=body.user_id)
    orders = []
    stocks = []
    for order in res.orders:
        orders.append(Order(price=order.price, number_of_stocks=order.number_of_stocks, stock_id=order.stock_id, created_at=order.created_at, type=order.type))
    for stock in res.stocks:
        stocks.append(Stock(stock_id=stock.stock_id, number=stock.number))
    return FindUserResponse(name=res.name, fund=res.fund, orders=orders, stocks=stocks)

@user.put('/deposit', status_code=200)
async def deposit_amount(body: FundUserRequest):
    res = User.objects.get(id=body.user_id)
    User.objects(id=body.user_id).update(fund=body.amount+res.fund)
    return "ok"

@user.put('/withdraw', status_code=200)
async def withdraw_amount(body: FundUserRequest):
    res = User.objects.get(id=body.user_id)
    if body.amount <= res.fund:
      User.objects(id=body.user_id).update(fund=res.fund-body.amount)
    return "ok"
