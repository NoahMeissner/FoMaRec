import requests
import json

def request_api(recipe):
    api_url = "https://smarthome.uni-regensburg.de/naehrwertrechner/api/1.0/"  
    endpoint = api_url + "recipe_info_optifast"
    
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'recipe': recipe
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status() 
        data = response.json()  
        return data
    except requests.exceptions.RequestException as e:
        print("Fehler: ", e)
