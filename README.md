# stock-trading

Steps to run the project:
1.  docker-compose up -d
2.  python3 migration.py (optional: to create users)
3.  python3 consumer.py 
4.  python3 scheduler.py
5.  uvicorn main:app --reload
