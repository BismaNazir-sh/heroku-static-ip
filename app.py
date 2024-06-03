import os
import pymongo
import socks
import socket
import ssl
import logging

# pymongo==3.12.3
# dnspython==2.2.1
# django-environ==0.10.0
# requests==2.25.1
# pysocks==1.7.1
try:
    import environ

    env = environ.Env()
    environ.Env.read_env()
except:
    pass


MONGODB_URI = env.str('MONGODB_URI', default="mongodb+srv://Bisma:Bisma123@cluster0.r1tthak.mongodb.net/")
QUOTAGUARDSTATIC_URL = env.str('QUOTAGUARDSTATIC_URL')

# Parse QuotaGuard Static URL
proxy_url = QUOTAGUARDSTATIC_URL.replace('http://', '').replace('https://', '')
proxy_auth, proxy_hostport = proxy_url.split('@')
proxy_host, proxy_port = proxy_hostport.split(':')
proxy_port = int(proxy_port)
proxy_username, proxy_password = proxy_auth.split(':')

# Configure the SOCKS5 proxy
socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port, username=proxy_username, password=proxy_password)
socket.socket = socks.socksocket

# Force TLS version
ssl_context = ssl.create_default_context()
ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # Optional: disable older TLS versions if necessary

def get_data():
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI, ssl=True, ssl_cert_reqs=ssl.CERT_NONE, ssl_context=ssl_context)
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
#     print("Response status code:", response.status_code)
#     print("Your outbound IP is:", response.json()["origin"])
# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")
