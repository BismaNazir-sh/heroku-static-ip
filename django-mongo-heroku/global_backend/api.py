import json
import requests
from logging import error
from pharmacy.auth import verification as auth
from pharmacy_terminal.globalConfig.heroku_config_vars import GB_APP_HEROKU_DOMAIN
from pharmacy.utils import JSONSerializer

customer_enhanced_api = f'{GB_APP_HEROKU_DOMAIN}/customer_enhanced_orders'
doctors_api = f'{GB_APP_HEROKU_DOMAIN}/doctors'


def find_doctors(filters: dict, attributes: dict):
    """
    Api to find all doctors.

    Args:
        filters: params to filter by
        attributes: attributes to fetch

    Returns:
        dict containing data
    """
    result = auth.get_token(app_name='sea-turtle')
    if result['success'] == 0:
        return result

    app_token = result['data'].get('app_token')
    if not app_token:
        return {'success': 0, 'data': {}, 'message': 'No app token found', 'error_code': 11.1}

    body = {
        'query_params': {'filters': filters, 'attributes': attributes}
    }
    headers = {'token': app_token}
    url = f'https://{doctors_api}/find/'
    response = requests.post(url=url, json=json.loads(json.dumps(body, cls=JSONSerializer)), headers=headers)
    if response.status_code == 200:
        try:
            res = response.json()
            data = res.get('data')
        except Exception as e:
            error(f'Exception: find_doctors. Message: could not get response {e}')
            return {'success': 0, 'data': {}, 'message': 'could not get response', 'error_code': 11.2}
    else:
        error(f'Exception: find_doctors. Message: Invalid response {response.text}')
        return {'success': 0, 'data': {}, 'message': 'No Invalid response', 'error_code': 11.3}

    if not data:
        error('Exception: find_doctors. Message: no data found')
        return {'success': 0, 'data': {}, 'message': 'No doctors found', 'error_code': 11.4}

    return {'success': 1, 'data': data, 'message': 'Success', 'error_code': 0}


def find_one_customer_enhanced_order(filters: dict, attributes: dict):
    """
    Api to find a customer_enhanced order from the customer_enhanced collection in gb database.

    Args:
        filters: params to filter by
        attributes: attributes to fetch

    Returns:
        dict containing data
    """
    result = auth.get_token(app_name='sea-turtle')
    if result['success'] == 0:
        return result

    app_token = result['data'].get('app_token')
    if not app_token:
        return {'success': 0, 'data': {}, 'message': 'No app token found', 'error_code': 10.1}

    body = {
        'query_params': {'filters': filters, 'attributes': attributes}
    }
    headers = {'token': app_token}
    url = f'https://{customer_enhanced_api}/find_one/'
    response = requests.post(url=url, json=json.loads(json.dumps(body, cls=JSONSerializer)), headers=headers)
    if response.status_code == 200:
        try:
            res = response.json()
            data = res.get('data')
        except Exception as e:
            error(f'Exception: find_one_customer_enhanced_order. Message: could not get response {e}')
            return {'success': 0, 'data': {}, 'message': 'could not get response', 'error_code': 10.2}
    else:
        error(f'Exception: find_one_customer_enhanced_order. Message: Invalid response {response.text}')
        return {'success': 0, 'data': {}, 'message': 'No Invalid response', 'error_code': 10.3}

    if not data:
        error('Exception: find_one_customer_enhanced_order. Message: no data found')
        return {'success': 0, 'data': {}, 'message': 'No order found', 'error_code': 10.4}

    return {'success': 1, 'data': data, 'message': 'Success', 'error_code': 0}


def update_one_customer_enhanced_order(filters: dict, values: dict, upsert: bool = False):
    """
    Api to update a customer_enhanced order in the customer_enhanced collection in gb database.

    Args:
        filters: params to filter by
        values: attributes to fetch
        upsert: should upsert?

    Returns:
        dict containing data
    """
    result = auth.get_token(app_name='sea-turtle')
    if result['success'] == 0:
        return result

    app_token = result['data'].get('app_token')
    if not app_token:
        return {'success': 0, 'data': {}, 'message': 'No app token found', 'error_code': 10.1}

    body = {
        'query_params': {'filters': filters, 'values': values, 'upsert': upsert}
    }
    headers = {'token': app_token}
    url = f'https://{customer_enhanced_api}/update_one/'
    response = requests.post(url=url, json=json.loads(json.dumps(body, cls=JSONSerializer)), headers=headers)
    if response.status_code != 200:
        error(f'Exception: update_one_customer_enhanced_order. Message: Invalid response {response.text}')
        return {'success': 0, 'data': {}, 'message': 'Invalid response', 'error_code': 10.3}

    return {'success': 1, 'data': {}, 'message': 'Order updated', 'error_code': 0}
