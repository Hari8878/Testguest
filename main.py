from flask import Flask, jsonify
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

@app.route("/register", methods=["GET"])  # allow GET so you can just visit in browser
def register():
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

    try:
        resp = requests.post(url, data=payload, headers=headers, timeout=10)
        return jsonify({
            "password_used": passwords,
            "signature": signature,
            "response_status": resp.status_code,
            "response": resp.text
        }), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1080, debug=False)
