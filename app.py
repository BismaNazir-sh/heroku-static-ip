from pymongo import MongoClient
import os
import pymongo
import socks
import socket
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    import environ

    env = environ.Env()
    environ.Env.read_env()
except:
    pass

try:
    MONGODB_URI = env.str('MONGODB_URI', default="mongodb+srv://Bisma:Bisma123@cluster0.r1tthak.mongodb.net/")
    client = MongoClient(MONGODB_URI)
    db = client['sea-turtle']
    QUOTAGUARDSTATIC_URL = env.str('QUOTAGUARDSTATIC_URL')

    # Parse QuotaGuard Static URL
    proxy_url = QUOTAGUARDSTATIC_URL.replace('http://', '').replace('https://', '')
    proxy_host, proxy_port = proxy_url.split('@')[1].split(':')[0], int(proxy_url.split('@')[1].split(':')[1])

    # Configure the SOCKS5 proxy
    socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port, username=proxy_url.split('@')[0].split(':')[0], password=proxy_url.split('@')[0].split(':')[1])
    socket.socket = socks.socksocket

    def get_data():
        
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client['sea-turtle']

        # Replace 'drugs' with the name of your collection
        collection = db['drugs']
        data = collection.find()
        data_list = list(data)
        for item in data_list:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
            logger.info(f'Item: {item}')
        return data_list
except Exception as e:
        logger.error(f"Failed to fetch data: {e}")

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
