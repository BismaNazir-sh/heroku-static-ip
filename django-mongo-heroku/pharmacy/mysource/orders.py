import time
from datetime import datetime
import datetime as dt

from pharmacy.utils import JSONSerializer
from pharmacy_terminal.globalConfig.mongo_client import *
import json
from bson.json_util import dumps
import re
from bson import ObjectId
from pharmacy.mysource.filling import update_ce_fill_function
from global_backend import api as global_backend_api
from math import ceil

orders_collection = mydatabase_pharmacy_terminal['orders']
pharmacy_collection = mydatabase_pharmacy_terminal['pharmacy']
pharmacists_collection = mydatabase_pharmacy_terminal['pharmacists']
drugs_collection = mydatabase_pharmacy_terminal['drugs']
#=====================================================================================================================

def fetch_all_orders_data_function(incoming_json_data):
    print("======================================FETCH ALL ORDERS DATA FUNCTION==================================")
    print("incoming_json_data",incoming_json_data)
    
    #Convert start_date and end_date to timestamp
    start_date = incoming_json_data['startDate']
    date = datetime.strptime(start_date, "%Y-%m-%d")
    start_date_timestamp = int(time.mktime(date.timetuple()) * 1000)

    end_date = incoming_json_data['endDate']
    date = datetime.strptime(end_date, "%Y-%m-%d")
    end_date_timestamp = int(time.mktime(date.timetuple()) * 1000)
    one_day_milliseconds = 24 * 60 * 60 * 1000
    end_date_timestamp = end_date_timestamp + one_day_milliseconds

    doctor = incoming_json_data['doctor']
    status = incoming_json_data['status']
    search_value = incoming_json_data['search_value']
    address_validation_failed = incoming_json_data.get("address_validation_failed", "")
    role = incoming_json_data['role']
    page = incoming_json_data['page']
    
    #drugs is for drug filter
    try:
        drugs = incoming_json_data['drugs']
    except:
        drugs = ""


    #extra status is for bulk ship as it wants complete_filled and label created both initially
    try:
        extra_status = incoming_json_data['extra_status']
    except:
        extra_status = ""
    
    #priority is for priority orders
    try:
        priority = incoming_json_data['priority']
    except:
        priority = ""

    try:
        pharmacy = incoming_json_data['pharmacy']
    except:
        pharmacy = ""



    items_per_page = 20
    skip = items_per_page * (page - 1)


    or_list = []
    match_conditions = []

    # Common match_statement for both roles
    if(status and status!="Refill"):
        match_conditions.append({
            "creation_timeStamp": {
                "$gte": start_date_timestamp,
                "$lte": end_date_timestamp
            }
        })
    if(status and status=="Refill"):
        match_conditions.append({
            "next_refill_timeStamp": {
                "$lte": end_date_timestamp+86400000
            }
        })

    if pharmacy and pharmacy != "":
        match_conditions.append({"pharmacy_ncpdpid": pharmacy})

    #Addign search based on status
    if(status !=""):
        if(status=="Refill"):
            match_conditions.append({"$or": [{"next_refill_timeStamp":{"$gt":0}}]})
        elif(extra_status!=""):
            match_conditions.append({"$or": [{"status": status}, {"status": extra_status}]})
        else:
            status_regex = re.compile(re.escape(status), re.IGNORECASE)
            match_conditions.append({"status": status_regex})

    if(priority!=""):
        #17 digit unix time stamp of 48hrs before current time
        threshold_timestamp = int(time.time()*1000) - 172800000
        
        match_conditions.append({"fills":{"$elemMatch":{"fill_status":"LABEL_CREATED",
                                                        "statusHistory.LABEL_CREATED.timeStamp":{"$lt": threshold_timestamp}}}})


    if(doctor!=""):
        doctor = doctor.strip()
        match_conditions.append({"scripts.doctor": int(doctor)})

    if(drugs!=""):
        drugs = drugs.strip()
        parts = drugs.rsplit(' ', 2)
        print("parts", parts)
        name = ' '.join(parts[:-2])
        qty = parts[-2]
        
        #Convert the int value to 3 decimal places
        try:
            qty = float(qty)
            if qty.is_integer():
                qty = "{:.3f}".format(qty)
            else:
                qty = qty
        except Exception as e:
            print("Error in converting qty to decimal", e)
            qty = qty
        unit = parts[-1]
        match_conditions.append({'$and':[{"scripts.name": name},{"scripts.dispense_quantity": str(qty)},{"scripts.dispense_unit": unit}]})
 
    #For address validation orders tab
    if address_validation_failed:
        match_conditions.append({"address_validation_failed": True})
        
    #searching...
    if(search_value.strip()!=""):

        #search in orderid
        order_id = search_value.strip()
        if(order_id !=""):
            order_id_regex = re.compile(re.escape(order_id), re.IGNORECASE)
            try:
                if(order_id_regex != ""):
                    order_id_regex = int(order_id)
                or_list.append({"order_id":order_id_regex})
            except:
                pass
        
        #search in patient
        patient = search_value.strip()
        if(patient !=""):
            try:
                patient_first_name, patient_last_name = patient.split()
                patient_first_name_regex = re.compile(re.escape(patient_first_name), re.IGNORECASE)
                patient_last_name_regex = re.compile(re.escape(patient_last_name), re.IGNORECASE)
                or_list.append({"$and": [
                    {"firstName": patient_first_name_regex},
                    {"lastName": patient_last_name_regex}
                ]
                })
            except:
                patient_regex = re.compile(re.escape(patient), re.IGNORECASE)
                or_list.append({"$or": [
                    {"firstName": patient_regex},
                    {"lastName": patient_regex}
                ]})

        #search in DOB
        dob = search_value.strip()
        if(dob !=""):
            dob_regex = re.compile(re.escape(dob), re.IGNORECASE)
            or_list.append({"dob": dob_regex})

        #search in email
        email = search_value.strip()
        if(email !=""):
            email_regex = re.compile(re.escape(email), re.IGNORECASE)
            or_list.append({"email": email_regex})

        #search in phone
        phone = search_value.strip()
        if(phone !=""):
            phone_regex = re.compile(re.escape(phone), re.IGNORECASE)
            or_list.append({"phoneNumber": phone_regex})            

    # If it is not super admin, add specific match_statement
    if role != 'super_admin':
        user = user_collection.find_one({"username": incoming_json_data['username']})
        if not user:
            return {'success':0, 'data':{}, 'message':'user not found', 'error_code':1}
        else:
            ncpdpid = str(user['pharmacy_ncpdpid'])
            pharmacy = ncpdpid
            print("ncpdpid",ncpdpid)
            match_conditions.append({"pharmacy_ncpdpid" : ncpdpid})
    
    if(search_value.strip()!=""):
        match_conditions.append({"$or": or_list})
    
    if(match_conditions != []):
        match_statement = {"$and": match_conditions}
    else:
        match_statement = {}

    print("match_statement",match_statement)
            
    count_pipeline = [
                        {"$match": match_statement},
                        {"$count": "total"}
                     ]
    try:
        count_result = orders_collection.aggregate(count_pipeline)
        total_count = list(count_result)[0]['total']
    except:
        total_count = 0

    #for downloading csv
    if(page==99999):
       skip = 0
       items_per_page = 99999
    print(match_statement)
    data_pipeline = [
    {"$match": match_statement},
    {"$sort": {"creation_timeStamp": -1}},
    {"$skip": skip},
    {"$limit": items_per_page},
    {"$project": {
            "_id": 0,
            "Order Id": "$order_id",
            "Status": "$status",
            "Received At":"$order_recieved_at",
            "Cancelled At":"$statusHistory.CANCELLED.timeStamp",
            "Refill Due Date":"$next_refill_timeStamp",
            "Patient":{"$concat": ["$firstName", " ", "$lastName"]},
            "DOB": "$dob",
            "Drug Info": {
                "$map": {
                    "input": "$scripts",
                    "as": "item",
                    "in": {
                        "drug": "$$item.name",
                        "quantity": {
                            "$concat": [
                                {
                                    "$toString": {
                                        "$divide": [
                                            {"$trunc": {"$multiply": [{"$toDouble": "$$item.dispense_quantity"}, 10]}},
                                            10
                                        ]
                                    }
                                },
                                " ",
                                "$$item.dispense_unit"
                            ]
                        }
                        }
                }
            }
            #,"Pharmacy": "$scripts.pharmacy",
        }
        }
    ]

    result = list(orders_collection.aggregate(data_pipeline))
    
    # Convert 'Cancelled At' timestamp to date
    for i in range(len(result)):
        
        if 'Cancelled At' in result[i]:
            row_timestamp = int(result[i]['Cancelled At']/1000)
            row_date = dt.datetime.fromtimestamp(row_timestamp)
            result[i]['Cancelled At'] = str(row_date)
        

        if 'Refill Due Date' in result[i] and result[i]['Refill Due Date']!="":
            row_timestamp = int(result[i]['Refill Due Date']/1000)
            row_date = dt.datetime.fromtimestamp(row_timestamp)
            result[i]['Refill Due Date'] = str(row_date)

        '''
        #If you dont want to show refill date in normal orders
        if status != "Refill":
            if 'Refill Due Date' in result[i]:
                del result[i]['Refill Due Date']
        '''

        #if pharmacy is allmed
        if(str(pharmacy) == "5717270"):
            for j in range(len(result[i]['Drug Info'])):
                try:
                    temp_number = result[i]['Drug Info'][j]['quantity'].split(" ")[0]
                    temp_unit = result[i]['Drug Info'][j]['quantity'].split(" ")[1]
                    temp_number = ceil(float(temp_number))
                    result[i]['Drug Info'][j]['quantity'] = str(temp_number) + " " + temp_unit
                except Exception as e:
                    print("Error in converting quantity to ceil", e)
                    result[i]['Drug Info'][j]['quantity'] = result[i]['Drug Info'][j]['quantity']
                    
    print("results",len(result))
    results_json = dumps(result)
        
    return {'success':1, 'data':results_json, 'total_count':total_count, 'message':'success', 'error_code':0}

#=====================================================================================================================
#=====================================================================================================================
#=====================================================================================================================

def show_order_details_function(incoming_json_data):
    print("======================================SHOW ORDER DETAILS FUNCTION==================================")
    print("incoming_json_data",incoming_json_data)
    order_id = incoming_json_data['order_id']
    username = incoming_json_data['username']

    print("order_id",order_id)
    print("username",username)
    
    user = user_collection.find_one({"username": username})
    if not user:
        return {'success':0, 'data':{}, 'message':'user not found', 'error_code':1}
    
    pharmacy = ""
    if(user['role'] == 'super_admin'):
        order = orders_collection.find_one({"order_id": int(order_id)})
    else:
        ncpdpid = str(user['pharmacy_ncpdpid'])
        order = orders_collection.find_one({"order_id": int(order_id), "pharmacy_ncpdpid": ncpdpid})
    
    pharmacy = order['pharmacy_ncpdpid']


    if not order:
        return {'success':0, 'data':{}, 'message':'order not found', 'error_code':1}

    order['physician_info'] = {
        'clinic': 'MD Exam',
        'npi': '',
        'license': 'T2623',
        'address': '4848 SW 74th Ct Ste 200, Miami FL, 33155',
        'phoneNumber': '833-210-4080'
    }
    order['patient_info'] = {
        'name': f"{order['firstName']} {order['lastName']}",
        'phoneNumber': order['phoneNumber'],
        'email': order['email'],
        'dob': '-'.join(order['dob'].split('/')),
        'address': f"{order['address']['address']}, {order['address']['city']} {order['address']['state']}, {order['address']['zipCode']} US",
        'gender': '',
        'medical_info': '',
        'allergies': '',
        'diagnosis': ''
    }
    order['prescription_info'] = {
        'order_id': order['order_id'],
        'id': str(order['_id']),
        'scripts': []
    }

    dob_year, dob_month, dob_day = order['dob'].split('/')
    order['lower_label_info'] = {
        'title': f"{order['firstName']} {order['lastName']} (DOB: {dob_day}/{dob_month}/{dob_year})",
        'drug_name': '',
        'subtitle': '',
        'use_by_date': ''
    }

    drugs = list(drugs_collection.find({}, {'_id': 0, 'clinic_drugname': 1, 'clinic_sig': 1, 'pharmacy_sig': 1, 'pharmacy_drugname':1, 'pharmacy_ncpdpid': 1}))

    if('scripts' in order):
        for i in range(len(order['scripts'])):
            order['scripts'][i]['_id'] = str(order['scripts'][i]['_id'])
            order['scripts'][i]['dosage_units'] = str(order['scripts'][i]['dosage_units'])

            if(pharmacy=="5717270"):
                order['scripts'][i]['dispense_quantity'] = ceil(float(str(order['scripts'][i]['dispense_quantity'])))

            #remove drafted from scripts
            if('drafted' in order['scripts'][i]):
                del order['scripts'][i]['drafted']

            ts = int(order['scripts'][i]['timeStamp'] / 1000.0)
            external_id = str(order['scripts'][i]['_id'])
            drug_name = order['scripts'][i]['name']
            if('sig' in order['scripts'][i]):
                drug_sig = order['scripts'][i]['sig']
            elif('signature_note' in order['scripts'][i]):
                drug_sig = order['scripts'][i]['signature_note']
            else:
                drug_sig = ''
                
            
            drug = [d for d in drugs if d['clinic_drugname'] == drug_name and d['clinic_sig'] == drug_sig]
            alt_sig = drug[0]['pharmacy_sig'] if drug else drug_sig
            pharmacy_drug_name = drug[0]['pharmacy_drugname'] if drug else drug_name
            
            
            script = {'date_written': datetime.fromtimestamp(ts).strftime('%Y-%m-%d'),
                      'name': drug_name, 'type': 'new rx', 'refills': order['scripts'][i]['number_refills'],
                      'external_id': external_id, 'product_id': '', 'batch': '', 'beyond_use_date': '', 'sig': alt_sig}
            order['prescription_info']['scripts'].append(script)
            order['physician_info']['name'] = order['scripts'][i]['doctor_name']

            if 'syringe' not in drug_name.lower():
                order['lower_label_info']['drug_name'] = pharmacy_drug_name
                order['lower_label_info']['subtitle'] = alt_sig
    
    pharmacists = list(pharmacists_collection.find({}, {'_id': 0, 'pharmacist_id': 1, 'pharmacy_ncpdpid': 1, 'first_name': 1, 'last_name': 1, 'phone': 1, 'email': 1}))
    pharmacists = [p for p in pharmacists if p['pharmacy_ncpdpid'] == order['pharmacy_ncpdpid']]

    if('fills' in order):
        for i in range(len(order['fills'])):
            order['fills'][i]['fill_id'] = int(order['fills'][i]['fill_id'])
            #for allmed pharmacy
            if(pharmacy=="5717270"):
                for j in range(len(order['fills'][i]['items'])):
                    order['fills'][i]['items'][j]['dispense_quantity'] = ceil(float(str(order['fills'][i]['items'][j]['dispense_quantity'])))

            if 'pharmacist_id' in order['fills'][i]:
                    pharmacist = [p for p in pharmacists if p['pharmacist_id'] == order['fills'][i]['pharmacist_id']]
                    if pharmacist:
                        order['fills'][i]['pharmacist'] = f"{pharmacist[0]['first_name'][0]}{pharmacist[0]['last_name'][0]}".upper()
    
    print("order found")
    print("order",order['_id'])

    #get weights and dimensions and add to order
    pharmacy_ncpdpid = order['pharmacy_ncpdpid']
    temp_pharmacy = pharmacy_collection.find_one({"ncpdpid": pharmacy_ncpdpid})
    if(temp_pharmacy):
        attribute_list = ['dim1','dim2','dim3','weight', 'is_fedex', 'integrated_label']
        for temp_attribute in attribute_list:
            if(temp_attribute in temp_pharmacy):
                order[temp_attribute] = temp_pharmacy.get(temp_attribute)

    order['pharmacy_info'] = {
        'name': temp_pharmacy['name'],
        'address': temp_pharmacy['address'],
        'phoneNumber': temp_pharmacy['phoneNumber'],
        'is_fedex': str(temp_pharmacy.get('is_fedex', False)),
        'integrated_label': str(temp_pharmacy.get('integrated_label', False)),
        'upper_label_positioning': temp_pharmacy.get('upper_label_positioning', {}),
        'lower_label_positioning': temp_pharmacy.get('lower_label_positioning', {}),
        'reviewed_on': '',
        'dispensed_on': '',
        'dispensing_notes': '',
        'tracking_number': '',
        'pharmacy_license': 'US',
        'ncpdpid': temp_pharmacy['ncpdpid'],
        'pic': '',
        'pic_license': '',
        'pharmacist': '',
        'tech': ''
    }

    data = json.loads(json.dumps(order, cls=JSONSerializer))
    return {'success':1, 'data':data, 'message':'success', 'error_code':0}



def mark_order_function(incoming_json_data):
    print("======================================MARK ORDER FUNCTION==================================")
    try:
        print("incoming_json_data",incoming_json_data)
        order_id = incoming_json_data['order_id']
        username = incoming_json_data['username']
        personal_code = incoming_json_data['personal_code']
        comment = incoming_json_data['comment']
        user = user_collection.find_one({"username": username})
        order_status = incoming_json_data['order_status']
        if not user:
            return {'success':0, 'data':{}, 'message':'user not found', 'error_code':11}
        
        if(user['role'] == 'super_admin'):
            order = orders_collection.find_one({"$or":[{"fills.fill_order_id":ObjectId(order_id)}]})    
            if(not order):
                order = orders_collection.find_one({"$or":[{"internal_order_id": str(order_id)}]})    
        
        elif((user['role'] == 'super_admin') or (user['role'] == 'pharmacy_admin')):
            ncpdpid = str(user['pharmacy_ncpdpid'])
            order = orders_collection.find_one({"$or":[{"fills.fill_order_id":ObjectId(order_id)}], "pharmacy_ncpdpid": ncpdpid})        
            if(not order):
                order = orders_collection.find_one({"$or":[{"internal_order_id": str(order_id)}], "pharmacy_ncpdpid": ncpdpid})        
                
        
        else:
            return {'success':0, 'data':{}, 'message':'user not authorized', 'error_code':13}
        
        if not order:
            return {'success':0, 'data':{}, 'message':'order not found', 'error_code':14}
        else:
            print("order found")
            print("order_id",order['_id'])
        
        #Return if order is already completed
        final_status_list = ['COMPLETED','CANCELLED']
        for temp_status in final_status_list:
            if(temp_status in order['statusHistory']):
                return {'success':0, 'data':{}, 'message':'order already completed', 'error_code':15}

        #cancel the entire order
        if('fills' not in order):
            status_history_record = order['statusHistory']

            status_history_record[order_status] = {}
            status_history_record[order_status]={ "timeStamp":int(time.time()*1000), "user":username, "personal_code":personal_code,"comment":comment}
            newvalues = { "$set": { "status": order_status, "statusHistory": status_history_record } }

            #update order
            myfilter = {"internal_order_id": str(order_id)}
            orders_collection.update_one(myfilter, newvalues)

            #update order in mdexam
            myfilter = {"orders._id": ObjectId(str(order_id))}
            issue_at_pharmacy = {
                "timeStamp":int(time.time()*1000),
                "user":username,
                "personal_code":personal_code,
                "comment":"ORDER CANCELLED reason:"+comment,
                "pharmacy":order['pharmacy']
            }
            # Find the order
            filters = {"orders._id": ObjectId(str(order_id))}
            attributes = {"orders.$": 1}
            result = global_backend_api.find_one_customer_enhanced_order(filters, attributes)
            if result['success'] == 0:
                return {'success': 0, 'data': {}, 'message': 'No order found', 'error_code': 10.1}

            order = result['data']['orders'][0]

            statusHistory = order['metadata']['statusHistory']
            statusHistory["ISSUE_AT_PHARMACY"] = issue_at_pharmacy
            values = { "$set": { "orders.$.metadata.internalOrderStatus": "ISSUE_AT_PHARMACY",
                                    "orders.$.metadata.statusHistory":statusHistory} }
            result = global_backend_api.update_one_customer_enhanced_order(filters, values)
            if result['success'] == 0:
                return {'success': 0, 'data': {}, 'message': 'Could not update order', 'error_code': 10.2}

            return {'success':1, 'data':{}, 'message':'success', 'error_code':0}

        #cancel a particular fill
        if('fills' in order):
            myfilter = {"fills.fill_order_id": ObjectId(order_id)}
            if(order_status == 'CANCELLED'):
                newvalues = { "$set": { "fills.$.fill_status": order_status, "fills.$.cancel_comment":comment, "fills.$.cancel_timeStamp":int(time.time()*1000), "fills.$.cancel_user":username, "fills.$.cancel_personal_code":personal_code, } }
            else:
                newvalues = { "$set": { "fills.$.fill_status": order_status } }
            orders_collection.update_one(myfilter, newvalues)


            temp_fill = orders_collection.find_one({"fills.fill_order_id": ObjectId(order_id)},{"fills.$":1})['fills'][0]
            temp_fill_id = temp_fill['fill_id']
            temp_order_id = temp_fill['fill_order_id']
            print("temp_order_id",temp_order_id)
            #update order in mdexam
            myfilter = {"orders._id": ObjectId(str(temp_order_id))}
            issue_at_pharmacy = {
                "timeStamp":int(time.time()*1000),
                "user":username,
                "personal_code":personal_code,
                "comment":"ORDER CANCELLED reason:"+comment,
                "pharmacy":order['pharmacy']
            }
            # Find the order
            filters = {"orders._id": ObjectId(str(temp_order_id))}
            attributes = {"orders.$": 1}
            result = global_backend_api.find_one_customer_enhanced_order(filters, attributes)
            if result['success'] == 0:
                return {'success': 0, 'data': {}, 'message': 'No order found', 'error_code': 10.1}

            order = result['data']['orders'][0]
            statusHistory = order['metadata']['statusHistory']
            print("statusHistory",statusHistory)
            statusHistory["ISSUE_AT_PHARMACY"] = issue_at_pharmacy
            values = { "$set": { "orders.$.metadata.internalOrderStatus": "ISSUE_AT_PHARMACY",
                                    "orders.$.metadata.statusHistory":statusHistory} }
            result = global_backend_api.update_one_customer_enhanced_order(filters, values, upsert=True)
            if result['success'] == 0:
                return {'success': 0, 'data': {}, 'message': 'Could not update order', 'error_code': 10.2}
            
            update_ce_fill_function(temp_fill_id)
            return {'success':1, 'data':{}, 'message':'success', 'error_code':0}


    except Exception as e:
        print("Exception",e)
        return {'success':0, 'data':{}, 'message':'Exception', 'error_code':1}



#=====================================================================================================================
def main():
    #get_all_data()
    incoming_json_data = {
        }

    result = fetch_all_orders_data_function(incoming_json_data)
    print(result)
        
    print("I have completed my task")

#=====================================================================================================================

if __name__ == "__main__":
    main()