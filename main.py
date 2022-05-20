from fastapi import FastAPI
from mongoengine import *
from routes.user import user
from routes.stock import stock
# from scheduler import run_job

connect(host="localhost")

app = FastAPI()
app.include_router(user)
app.include_router(stock)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# run_job()