# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import requests, json, re, urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# ==========================================================
# =============== PROTOBUF PARSER (SHORT) ==================
# ==========================================================

def decode_varint(data, i=0):
    shift = result = 0
    while i < len(data):
        b = data[i]; i += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80): return result, i
        shift += 7
    return result, i

def _pretty_bytes(b):
    try:
        s = b.decode(); 
        if any(ord(c) < 32 and c not in '\r\n\t' for c in s): raise ValueError
        return s
    except: return b.hex()

def parse_protobuf(data):
    i, out = 0, {}
    while i < len(data):
        key, i = decode_varint(data, i)
        f, wt = key >> 3, key & 7
        if wt == 0: val, i = decode_varint(data, i)
        elif wt == 2:
            l, i = decode_varint(data, i); raw = data[i:i+l]; i += l
            try: val = parse_protobuf(raw)
            except: val = _pretty_bytes(raw)
        else: break
        out[f] = val
    return out

# ==========================================================
# =============== HELPERS ==================================
# ==========================================================

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
COOKIES = {"source": "pc", "language": "en"}

def get_open_idd(token):
    if not token: return None
    try:
        url = f"https://100067.connect.garena.com/oauth/token/inspect?token={token}"
        r = requests.get(url, headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(SM-A805N ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }, verify=False, timeout=10)
        return r.json().get("open_id") if r.ok else None
    except: return None

def get_real_access_token(token):
    try:
        r = requests.get(f"https://api-otrss.garena.com/support/callback/?access_token={token}",
                         headers=HEADERS, cookies=COOKIES, verify=False, allow_redirects=False, timeout=10)
        if "Location" in r.headers:
            m = re.search(r"access_token=([A-Fa-f0-9]+)", r.headers["Location"])
            if m: return m.group(1)
        if r.ok:
            j = r.json(); return j.get("access_token") or j.get("token")
    except: pass
    return None

def get_platform(token):
    try:
        url = f"https://ffmconnect.live.gop.garenanow.com/oauth/token/inspect?token={token}"
        r = requests.get(url, headers={"User-Agent": "GarenaMSDK/4.0.19P9"}, verify=False, timeout=10)
        return r.json().get("main_active_platform", 8) if r.ok else 8
    except: return 8

def encode_varint(n):
    b = []
    while n > 0x7F: b.append((n & 0x7F) | 0x80); n >>= 7
    b.append(n)
    return bytes(b)

def create_proto(fields):
    pkt = bytearray()
    for f, v in fields.items():
        if isinstance(v, int):
            pkt += encode_varint((f << 3) | 0) + encode_varint(v)
        else:
            val = v.encode() if isinstance(v, str) else v
            pkt += encode_varint((f << 3) | 2) + encode_varint(len(val)) + val
    return pkt

# ==========================================================
# =============== MAIN FLASK ROUTE =========================
# ==========================================================

@app.route('/ACS', methods=['GET'])
def acs_handler():
    token = request.args.get("token")
    if not token: return jsonify({"error": "Missing token"}), 400

    # Step 1: player info
    url1 = f"https://gamesecurity.freefireindiamobile.com/api/info?access_token={token}&lang=en&region=IND"
    r1 = requests.get(url1, headers=HEADERS, verify=False)
    try:
        data1 = r1.json(); uid = data1["data"]["player"]["uid"]; nickname = data1["data"]["player"]["nickname"]
    except: return jsonify({"error": "invalid token", "raw": r1.text}), 400

    # Step 2: shop2game + open_id fallback
    r2 = requests.post("https://shop2game.com/api/auth/player_id_login",
                       json={"app_id": 100067, "login_id": str(uid)}, headers=HEADERS)
    open_id = (r2.json().get("open_id") if r2.ok else None) or get_open_idd(token)

    # Step 3: Access token & platform
    access_token = get_real_access_token(token)
    platform = get_platform(access_token or token)

    # Step 4: Protobuf & AES
    proto = create_proto({29: access_token or "", 22: open_id or "", 99: str(platform), 100: str(platform)})
    cipher = AES.new(b'Yg&tc%DEuh6%Zc^8', AES.MODE_CBC, b'6oyZDr22E3ychjM%')
    enc = cipher.encrypt(pad(proto, AES.block_size))

    # Step 5: Send MajorLogin
    headers = {
        'X-Unity-Version': '2018.4.11f1', 'ReleaseVersion': 'OB51',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; Android 7.1.2)'
    }
    resp = requests.post("https://loginbp.ggblueshark.com/MajorLogin", data=enc, headers=headers)
    try: parsed = parse_protobuf(resp.content)
    except: parsed = {"raw_hex": resp.content.hex()}

    return jsonify({
        "uid": uid, "nickname": nickname, "open_id": open_id,
        "access_token": access_token, "platform": platform,
        "parsed": parsed
    })

# ==========================================================
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
