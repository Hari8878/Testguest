responseonseonse flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import random
import string

app = Flask(__name__)

# Generate random password
def generate_custom_password(random_length=8):
    characters = string.ascii_letters + string.digits
    random_part = ''.join(random.choice(characters) for _ in range(random_length)).upper()
    return f"Harimods{random_part}"

def send_request(password):
    key = b"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

    data_str = f"password={password}&client_type=2&source=2&app_id=100067"
    data = data_str.encode()
    signature = hmac.new(key, data, hashlib.sha256).hexdigest()

    payload = {
        'password': password,
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

    resp = requests.post(url, data=payload, headers=headers, timeout=10)
    return {
        "password_used": password,
        #"signature": signature,
        "response_status": resp.status_code,
        "response": resp.text
    }#, resp.status_code

@app.route("/register", methods=["GET"])
def register():
    password = generate_custom_password()
    return jsonify(*send_request(password))

@app.route("/custom", methods=["GET"])
def custom():
    password = request.args.get("password")
    if not password:
        return jsonify({"error": "Provide password with ?password=YOURPASS"}), 400
    return jsonify(*send_request(password))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1080, debug=False)
