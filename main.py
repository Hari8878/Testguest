from flask import Flask, render_template_string, request, jsonify
import requests, json
yy
app = Flask(__name__)

HEADERS = {
    "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 8 Pro;Android 11;en;IN;)",
    "Connection": "Keep-Alive",
    "Accept": "application/json",
    "Accept-Encoding": "gzip"
}

HTML_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Garena Bind Tool</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body{font-family:sans-serif;background:#f5f7fa;padding:20px;}
    .card{background:#fff;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,.1);padding:20px;max-width:600px;margin:auto;}
    input,button{padding:10px;font-size:14px;margin:5px 0;width:100%;border-radius:6px;border:1px solid #ccc;}
    button{background:#007bff;color:#fff;cursor:pointer;border:none;}
    button:hover{background:#0056b3;}
    pre{background:#111;color:#0f0;padding:10px;border-radius:8px;overflow:auto;}
    .success{color:#00ff00;font-weight:bold;}
    .error{color:#ff4444;font-weight:bold;}
  </style>
</head>
<body>
  <div class="card">
    <h2>Garena Bind Tool</h2>
    <input id="access_token" placeholder="Enter access_token">
    <input id="email" placeholder="Enter email (e.g. example@gmail.com)">
    <button onclick="sendOtp()">Send OTP</button>
    <input id="otp" placeholder="Enter OTP" style="display:none;">
    <button id="verifyBtn" onclick="verifyOtp()" style="display:none;">Verify & Bind</button>
    <button id="cancelBtn" onclick="cancelBind()">Cancel Bind</button>
    <pre id="output"></pre>
  </div>
  <script>
    async function post(endpoint, data) {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
      });
      return res.json();
    }

    function showOutput(obj, step) {
      const out = document.getElementById('output');
      if (obj.result === 0) {
        out.innerHTML = `<span class="success">✅ ${step} Success!</span>\\n` + JSON.stringify(obj, null, 2);
      } else {
        out.innerHTML = `<span class="error">❌ ${step} Failed</span>\\n` + JSON.stringify(obj, null, 2);
      }
    }

    async function sendOtp() {
      const access_token = document.getElementById('access_token').value.trim();
      const email = document.getElementById('email').value.trim();
      const out = document.getElementById('output');
      out.textContent = '📤 Sending OTP...';
      const res = await post('/send_otp', {access_token, email});
      showOutput(res, 'Send OTP');
      if (res.result === 0) {
        document.getElementById('otp').style.display = 'block';
        document.getElementById('verifyBtn').style.display = 'block';
      }
    }

    async function verifyOtp() {
      const access_token = document.getElementById('access_token').value.trim();
      const email = document.getElementById('email').value.trim();
      const otp = document.getElementById('otp').value.trim();
      const out = document.getElementById('output');
      out.textContent = '📤 Verifying OTP & Binding...';
      const res = await post('/verify_otp', {access_token, email, otp});
      showOutput(res, 'Verify + Bind');
    }

    async function cancelBind() {
      const access_token = document.getElementById('access_token').value.trim();
      const out = document.getElementById('output');
      out.textContent = '📤 Cancelling Bind Request...';
      const res = await post('/cancel_bind', {access_token});
      showOutput(res, 'Cancel Bind');
    }
  </script>
</body>
</html>
"""

def post(url, data):
    try:
        r = requests.post(url, data=data, headers=HEADERS, timeout=10)
        return json.loads(r.text)
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/send_otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    access_token = data.get("access_token")
    email = data.get("email")

    otp_resp = post("https://ffmconnect.live.gop.garenanow.com/game/account_security/bind:send_otp", {
        "app_id": "100067",
        "access_token": access_token,
        "email": email,
        "locale": "en_IN",
        "bind_type": "1",
        "platform": "android"
    })
    return jsonify(otp_resp)

@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    access_token = data.get("access_token")
    email = data.get("email")
    otp = data.get("otp")

    verify_resp = post("https://ffmconnect.live.gop.garenanow.com/game/account_security/bind:verify_otp", {
        "app_id": "100067",
        "access_token": access_token,
        "otp": otp,
        "email": email
    })

    if verify_resp.get("result") != 0:
        return jsonify({"result": 1, "message": "OTP verification failed", "verify_response": verify_resp})

    verifier_token = verify_resp.get("verifier_token")

    bind_resp = post("https://ffmconnect.live.gop.garenanow.com/game/account_security/bind:create_bind_request", {
        "app_id": "100067",
        "access_token": access_token,
        "verifier_token": verifier_token,
        "secondary_password": "B2FA5BC8C381DC0873E4201120A95255CF852C6D67A76A4E97307A3A031ADF3E",
        "email": email
    })

    return jsonify(bind_resp)

@app.route("/cancel_bind", methods=["POST"])
def cancel_bind():
    data = request.get_json()
    access_token = data.get("access_token")

    cancel_resp = post("https://ffmconnect.live.gop.garenanow.com/game/account_security/bind:cancel_request", {
        "app_id": "100067",
        "access_token": access_token
    })

    return jsonify(cancel_resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
