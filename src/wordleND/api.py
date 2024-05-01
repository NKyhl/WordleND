import requests
import json

def view_all_coins(access_token):
    headers = {
        'Authorization':f'Bearer {access_token}'
    }

    response = requests.get("https://jcssantos.pythonanywhere.com/api/group15/group15/", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to access the API endpoint to view all coins:", response.status_code)

def view_balance_for_user(access_token, email):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(f'https://jcssantos.pythonanywhere.com/api/group15/group15/player/{email}/', headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to access the API endpoint to view balance for user:", response.status_code)

def user_pay(access_token, email, amount):
    headers = {
        'Authorization':f'Bearer {access_token}'
    }
    data = {"amount":amount}

    response = requests.post(f"https://jcssantos.pythonanywhere.com/api/group15/group15/player/{email}/pay", headers=headers, data=data)

    if response.status_code == 200:
        return {'message':f'Successfully purchased {amount} games!'}
    else:
        print("Failed to access the API endpoint to pay:", response.status_code)
        return {'message':f'Insufficient Funds!'}