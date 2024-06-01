from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGODB_URI = "mongodb+srv://Bisma:Bisma123@cluster0.r1tthak.mongodb.net/"
client = MongoClient(MONGODB_URI)
db = client['sea-turtle']

@app.route('/data', methods=['GET'])
def get_data():
    collection = db['drugs']
    data = collection.find()
    data_list = list(data)
    for item in data_list:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string
    return jsonify(data_list)

if __name__ == '__main__':
    app.run(debug=True)
