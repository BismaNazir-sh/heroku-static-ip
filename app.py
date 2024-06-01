from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection string from environment variable
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client.get_database()

@app.route('/data', methods=['GET'])
def get_data():
    # Replace 'your_collection' with the name of your collection
    collection = db['your_collection']
    data = collection.find()
    data_list = list(data)
    for item in data_list:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string
    return jsonify(data_list)

if __name__ == '__main__':
    app.run(debug=True)
