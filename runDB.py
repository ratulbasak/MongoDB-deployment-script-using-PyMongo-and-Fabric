from pymongo import MongoClient

client = MongoClient('localhost:27017')
db = client.db-folder                  # db_name will be your db name
coll = db.dataset
db.add_user('db-folder', 'db-password', roles=["readWrite", "dbAdmin"])
