
import pymongo


try:
    import environ

    env = environ.Env()
    environ.Env.read_env()
except:
    pass

import socks
import socket
from urllib.parse import urlparse

MONGODB_URI = env.str('MONGODB_URI', default="mongodb+srv://Bisma:Bisma123@cluster0.r1tthak.mongodb.net/")
FIXIE_SOCKS_HOST = env.str('FIXIE_SOCKS_HOST')

fixie_url = urlparse(f"socks5://{FIXIE_SOCKS_HOST}")
proxy_username = fixie_url.username
proxy_password = fixie_url.password
proxy_host = fixie_url.hostname
proxy_port = fixie_url.port

# Configure the SOCKS5 proxy
socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port, username=proxy_username, password=proxy_password)
socket.socket = socks.socksocket


def get_data():
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(
            MONGODB_URI,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        db = client['sea-turtle']

        # Replace 'drugs' with the name of your collection
        collection = db['drugs']
        data = collection.find()
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
