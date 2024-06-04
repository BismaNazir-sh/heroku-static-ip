import socks
import socket
import pymongo

# Set up the SOCKS5 proxy
proxy_host = "us-east-static-02.quotaguard.com"
proxy_port = 9293  # Use the appropriate port from Quotaguard
proxy_username = "t8n4lainx2fmf4"
proxy_password = "6n3kugd661dpcoj7pzm5yu4w1k3"

socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port, username=proxy_username, password=proxy_password)
socket.socket = socks.socksocket

# MongoDB connection string
mongo_uri = "mongodb+srv://Bisma:Bisma123@cluster1.lham6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1&connectTimeoutMS=30000"

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)
db = client['sample_airbnb']
collection = db['listingsAndReviews']

# Example query
document = collection.find_one()
print(document)
