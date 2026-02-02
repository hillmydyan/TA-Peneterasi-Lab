import requests

GUACAMOLE_URL = "http://localhost:8080/guacamole"
USERNAME = "guacadmin"
PASSWORD = "guacadmin"

def get_guacamole_token():
    url = f"{GUACAMOLE_URL}/api/tokens"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json()["authToken"]
    else:
        return None
