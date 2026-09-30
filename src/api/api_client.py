import requests

def get_data():
    '''
    получаем данные
    '''
    data = requests.get('https://opensky-network.org/api/states/all', timeout=30)
    data.raise_for_status()
    return data.json()