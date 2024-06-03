
import pymongo


try:
    import environ

    env = environ.Env()
    environ.Env.read_env()
except:
    pass

MONGODB_URI = env.str('MONGODB_URI', default="mongodb+srv://Bisma:Bisma123@cluster0.r1tthak.mongodb.net/")
#MONGODB_URI = "mongodb+srv://Bisma:Bisma123@cluster1.lham6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
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
        for item in data_list:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
            print(f'Item: {item}')
        return data_list
    except Exception as e:
        print(f"Failed to fetch data: {e}")


if __name__ == '__main__':
        get_data()


# import os
# import requests

# # Fetch the QuotaGuard Static proxy URL from environment variable
# QUOTAGUARDSTATIC_URL = env.str('QUOTAGUARDSTATIC_URL')

# # Set up the proxies dictionary
# proxies = {
#     "http": QUOTAGUARDSTATIC_URL,
#     "https": QUOTAGUARDSTATIC_URL,
# }

# # URL to check outbound IP address
# external_url = 'http://httpbin.org/ip'

# try:
#     # Make a request to the external service
#     response = requests.get(external_url) #, proxies=proxies)
#     print("Response status code:", response)
#     print("Your outbound IP is:", response.json())
# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")
