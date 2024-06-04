import pymongo
MONGODB_URI = "mongodb+srv://Bisma:Bisma123@cluster1.lham6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
def get_data():
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
        return data_list
    except Exception as e:
        print(f"Failed to fetch data: {e}")


if __name__ == '__main__':
        get_data()