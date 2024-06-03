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
    try:
        collection = db['drugs']
        data = collection.find()
        data_list = list(data)
        for item in data_list:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
            print('item', item)
        return
    except Exception as e:
        print('errorrrrrrrrrrrrrrrrrrrrrrr', e)
        pass

    
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
#     print("Response status code:", response.status_code)
#     print("Your outbound IP is:", response.json()["origin"])
# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")
