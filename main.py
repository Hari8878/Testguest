import requests
import hmac
import hashlib
import random
import string

def generate_custom_password(random_length=8):
    characters = string.ascii_letters + string.digits
    random_part = ''.join(random.choice(characters) for _ in range(random_length)).upper()
    return f"Harimods{random_part}"

passwords = generate_custom_password()
key = b"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

data_str = f"password={passwords}&client_type=2&source=2&app_id=100067"
data = data_str.encode()

signature = hmac.new(key, data, hashlib.sha256).hexdigest()

payload = {
    'password': passwords,
    'client_type': "2",
    'source': "2",
    'app_id': "100067"
}

url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/register"

headers = {
    'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 8 Pro ;Android 11;en;IN;)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Authorization': "Signature " + signature
}

response = requests.post(url, data=payload, headers=headers)

print("Password used:", passwords)
print("Response      :", response.text)