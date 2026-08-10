from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_URL = "https://horizon.policyboss.com:5443/quote/pb_vehicle_info"

@app.get("/Vehicle")
def vehicle():
    reg_value = request.args.get("reg_value")
    token_value = request.args.get("token_value")

    if not reg_value or not token_value:
        return jsonify({
            "success": False,
            "error": "Missing reg_value or token_value"
        }), 400

    
    payload = {
  "secret_key": "SECRET-HZ07QRWY-JIBT-XRMQ-ZP95-J0RWP3DYRACW",
  "client_key": "CLIENT-CNTP6NYE-CU9N-DUZW-CSPI-SH1IS4DOVHB9",
  "RegistrationNumber": "TN93F9915",
  "product_id": 10,
  "ss_id": "0",
  "source": "PB-BETA-MOBILE",
  "session_id": reg_value,
  "g-recaptcha-response": token_value,
  "captcha": token_value
}

    response = requests.post(
        API_URL,
        json=payload,
        timeout=20
    )

    try:
        result = response.json()
        return jsonify(result), response.status_code
    except ValueError:
        return jsonify({
            "success": False,
            "response": response.text
        }), response.status_code


if __name__ == "__main__":
    app.run(debug=True)
