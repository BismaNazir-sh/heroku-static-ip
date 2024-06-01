mongo_client.py
import pymongo

from pymongo import MongoClient
from pharmacy_terminal.globalConfig.heroku_config_vars import *


try:

    mongo_uri = CONFIG_MONGO_URI
    client1 = MongoClient(mongo_uri,maxPoolSize=500)
    mydatabase_pharmacy_terminal = client1['sea-turtle']

    user_collection = mydatabase_pharmacy_terminal['user']
    pharmacy_collection = mydatabase_pharmacy_terminal['pharmacy']
    pharmacist_collection = mydatabase_pharmacy_terminal['pharmacists']
    orders_collection = mydatabase_pharmacy_terminal['orders']
    skypostal_logs_collection = mydatabase_pharmacy_terminal['skypostal_logs']
    myconfig_collection = mydatabase_pharmacy_terminal['myConfig']
    action_logs_collection = mydatabase_pharmacy_terminal['action_logs']



    
except Exception as e:
    print("@ Exeption occured creating mongo client cause",str(e))
