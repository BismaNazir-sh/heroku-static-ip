from pymongo import MongoClient

MONGODB_URI = "mongodb+srv://Bisma:Bisma123@cluster0.r1tthak.mongodb.net/"
client = MongoClient(mongo_uri)
db = client['sea-turtle']

def get_data():
    # Replace 'your_collection' with the name of your collection
    collection = db['drugs']
    data = collection.find()
    data_list = list(data)
    for item in data_list:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string
        print('item', item)
    return 

if __name__ == '__main__':
    get_data()
