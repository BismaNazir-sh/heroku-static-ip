from django.http import JsonResponse
from pymongo import MongoClient
import os
import pymongo


try:
    import environ

    env = environ.Env()
    environ.Env.read_env()
except:
    pass
MONGODB_URI = env.str('MONGODB_URI', default="mongodb+srv://Bisma:Bisma123@cluster0.r1tthak.mongodb.net/")

def get_data_from_mongodb(request):
    data_list=  []
    try:
        print("in try")
        # Connect to MongoDB
        client = pymongo.MongoClient(
            MONGODB_URI
        )
        db = client['sample_geospatial']
        print('got db')
        # Replace 'drugs' with the name of your collection
        collection = db['shipwrecks']
        data = collection.find({}).limit(10)
        print("got collection")
        data_list = list(data)
        print("got list")
        for item in data_list:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
            print(f'Item: {item}')
        return JsonResponse(data_list, safe=False)
    except Exception as e:
        print(f"Failed to fetch data: {e}")

    return JsonResponse(data_list, safe=False)
