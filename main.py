from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "api": "PAN to Info API",
        "usage": "/pan-info?pan=JCZPS4827P",
        "example": "/pan-info?pan=JCZPS4827P"
    })

@app.route("/pan-info", methods=["GET"])
def pan_info():
    pan = request.args.get("pan", "").strip().upper()

    if not pan or len(pan) != 10:
        return jsonify({
            "error": "Valid 10-digit PAN required",
            "example": "/pan-info?pan=JCZPS4827P"
        }), 400

    try:
        # Step 1: Token eduka
        token_url = "https://turtlemintloans.com/api/minterprise/v1/token/issue"
        token_headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 16; CPH2731 Build/BP2A.250605.015; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.192 Mobile Safari/537.36",
            'authorization': "Basic dHVydGxlZmluOnR1cnRsZWZpbjEyMw=="  # b64(turtlefin:turtlefin123)
        }
        
        token_resp = requests.get(token_url, headers=token_headers, timeout=10)
        token_resp.raise_for_status()
        token_data = token_resp.json()
        token = token_data["data"]["accessToken"]

        # Step 2: PAN data eduka
        pan_url = "https://turtlemintloans.com/api/minterprise/v1/products/personal-loan/leads/existing-lead-by-pan"
        pan_headers = {
            'authorization': f"Bearer {token}",
            'x-provider': "signzy",
            'User-Agent': token_headers['User-Agent']
        }
        pan_params = {'pan': pan}

        resp = requests.get(pan_url, params=pan_params, headers=pan_headers, timeout=15)

        if resp.status_code == 200:
            return jsonify(resp.json())
        else:
            return jsonify({
                "error": f"Upstream error {resp.status_code}",
                "raw_response": resp.text[:500]
            }), resp.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Request failed", "details": str(e)}), 500
    except KeyError:
        return jsonify({"error": "Token not found in response"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
