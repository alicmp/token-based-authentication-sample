import requests

BASE_URL = 'http://localhost:8000/{}'
PHONE_NUMBER = '09195379743'
PASSWORD = '1234'

# testing all the functionalities of project
def init_test():
    # testing login view
    data = {
        'phone_number': PHONE_NUMBER,
    }
    response = requests.post(url=BASE_URL.format('accounts/login/'), data=data)
    assert response.status_code == 200, "login view has problem!"

    # testing confirmation view
    data = {
        'phone_number': PHONE_NUMBER,
        'password': PASSWORD
    }
    response = requests.post(url=BASE_URL.format('accounts/confirmation/'), data=data)
    assert response.status_code == 200, "confirmation view has problem!"

    # testing authentication
    token = response.json().get('token')
    headers = {
        'Authorization': "Bearer {}".format(token),
    }
    response = requests.get(url=BASE_URL.format('accounts/test/'), headers=headers)
    assert response.status_code != 401, "authentication has problem!"

    print("Everything is fine!")

if __name__ == "__main__":
    init_test()
