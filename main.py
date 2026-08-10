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
headers = {
  'Host': "horizon.policyboss.com:5443",
  'User-Agent': "Mozilla/5.0 (Linux; Android 15; V2250 Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/152.0.7977.30 Safari/537.36",
  'Accept': "application/json, text/javascript, */*; q=0.01",
  'Accept-Encoding': "gzip, deflate, br, zstd",
  'sec-ch-ua-platform': "\"Android\"",
  'sec-ch-ua': "\"Chromium\";v=\"152\", \"Not?A_Brand\";v=\"24\", \"Android WebView\";v=\"152\"",
  'content-type': "application/json;charset=UTF-8",
  'sec-ch-ua-mobile': "?1",
  'origin': "https://www.policyboss.com",
  'x-requested-with': "mark.via.gp",
  'sec-fetch-site': "same-site",
  'sec-fetch-mode': "cors",
  'sec-fetch-dest': "empty",
  'referer': "https://www.policyboss.com/",
  'accept-language': "en-US,en;q=0.9",
  'priority': "u=1, i"
}

    response = requests.post(
        API_URL,
        json=payload,headers=headers,
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
