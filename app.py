from pymongo import MongoClient


try:
    import environ

    env = environ.Env()
    environ.Env.read_env()
except:
    pass

MONGODB_URI = env.str('MONGODB_URI', default="mongodb+srv://Bisma:Bisma123@cluster0.r1tthak.mongodb.net/")

client = MongoClient(MONGODB_URI)
db = client['sea-turtle']

def get_data():
    # Replace 'drugs' with the name of your collection
    collection = db['drugs']
    data = collection.find()
    data_list = list(data)
    for item in data_list:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string
        print('item', item)
    return

if __name__ == '__main__':
    get_data()
