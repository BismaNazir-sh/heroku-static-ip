import json
import base64
from logging import error
from bson.objectid import ObjectId
from datetime import datetime

def default(self, o):
    if isinstance(o, ObjectId):
        return str(o)
    return json.JSONEncoder.default(self, o)

class JSONSerializer(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def save_base64_encoded_pdf(encoded_pdf):
    """
    Decodes a Base64 encoded PDF and saves it to the specified output path.
    Parameters:
    - encoded_pdf: A string containing the Base64 encoded PDF.
    """
    try:
        # Decode the Base64 encoded PDF
        return base64.b64decode(encoded_pdf)
    except Exception as e:
        error(f"Error saving label: {e}")

def is_valid_date(date_str):
    is_valid = False
    valid_formats = ["%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d", "%Y-%m-%d"]
    for format in valid_formats:
        try:
            datetime.strptime(date_str, format)
            
            return True
        except ValueError:
            is_valid = False
    return is_valid