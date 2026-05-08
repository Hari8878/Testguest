import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template_string

app = Flask(__name__)

# ---------------- FETCH HSE RESULT ----------------

def fetch_hse_results(regno: str, dob: str) -> dict:

    url = "https://tnresults.nic.in/rdtpex.asp"

    payload = {
        "regno": regno,
        "dob": dob,
        "B1": "Get Marks"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://tnresults.nic.in/rdtpex.htm"
    }

    try:

        response = requests.post(
            url,
            data=payload,
            headers=headers,
            timeout=20
        )

        soup = BeautifulSoup(response.text, "html.parser")

        table_div = soup.find("div", class_="design")

        if not table_div:
            return {
                "status": False,
                "message": "No result found"
            }

        table = table_div.find("table")
        rows = table.find_all("tr")

        full_info = rows[0].find_all("td")[0].get_text(strip=True)

        match = re.search(
            r'^(.*?)\s+\(\s*(\d+)\s*\)',
            full_info
        )

        if match:
            student_name = match.group(1)
            register_number = match.group(2)
        else:
            student_name = "Unknown"
            register_number = regno

        subjects = []

        total_marks = ""
        overall_result = ""

        for row in rows[1:]:

            cols = row.find_all("td")

            if len(cols) < 6:
                continue

            first_col = cols[0].get_text(strip=True).upper()

            if "TOTAL" in first_col:

                total_marks = cols[4].get_text(strip=True)
                overall_result = cols[5].get_text(strip=True)

                continue

            subject = cols[0].get_text(strip=True)
            total = cols[4].get_text(strip=True)

            subjects.append({
                "subject": subject,
                "mark": total
            })

        return {
            "status": True,
            "name": student_name,
            "register_number": register_number,
            "subjects": subjects,
            "total_marks": total_marks,
            "result": overall_result
        }

    except Exception as e:

        return {
            "status": False,
            "message": str(e)
        }

# ---------------- HTML ----------------

HTML_PAGE = """

<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>TN HSE Result</title>

    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>

        *{
            margin:0;
            padding:0;
            box-sizing:border-box;
        }

        body{

            font-family:'Poppins',sans-serif;

            background:
            linear-gradient(
                135deg,
                #0f172a,
                #111827,
                #1e293b
            );

            min-height:100vh;

            display:flex;
            justify-content:center;
            align-items:center;

            padding:20px;

            overflow-x:hidden;
        }

        .bg{

            position:fixed;
            width:100%;
            height:100%;
            top:0;
            left:0;
            overflow:hidden;
            z-index:-1;
        }

        .circle{

            position:absolute;
            border-radius:50%;
            background:rgba(255,255,255,0.05);
            animation:float 10s infinite linear;
        }

        .circle:nth-child(1){
            width:200px;
            height:200px;
            left:10%;
            top:20%;
        }

        .circle:nth-child(2){
            width:300px;
            height:300px;
            right:10%;
            top:10%;
        }

        .circle:nth-child(3){
            width:150px;
            height:150px;
            bottom:10%;
            left:30%;
        }

        @keyframes float{

            0%{
                transform:translateY(0px) rotate(0deg);
            }

            50%{
                transform:translateY(-20px) rotate(180deg);
            }

            100%{
                transform:translateY(0px) rotate(360deg);
            }
        }

        .container{

            width:100%;
            max-width:520px;

            background:rgba(255,255,255,0.08);

            backdrop-filter:blur(20px);

            border:1px solid rgba(255,255,255,0.1);

            border-radius:25px;

            padding:30px;

            box-shadow:
            0 10px 40px rgba(0,0,0,0.4);

            color:white;
        }

        .title{

            text-align:center;
            margin-bottom:25px;
        }

        .title h1{

            font-size:32px;
            font-weight:700;

            background:linear-gradient(
                90deg,
                #60a5fa,
                #38bdf8,
                #818cf8
            );

            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
        }

        .title p{

            margin-top:8px;
            color:#cbd5e1;
            font-size:14px;
        }

        .input-box{

            margin-bottom:18px;
        }

        .input-box label{

            display:block;
            margin-bottom:8px;
            color:#e2e8f0;
            font-size:14px;
            font-weight:500;
        }

        input,
        select{

            width:100%;
            padding:14px 16px;

            border:none;

            outline:none;

            border-radius:14px;

            background:rgba(255,255,255,0.08);

            color:white;

            font-size:15px;

            transition:0.3s;
        }

        input:focus,
        select:focus{

            background:rgba(255,255,255,0.12);

            box-shadow:
            0 0 0 2px #3b82f6;
        }

        select option{
            color:black;
        }

        input::placeholder{
            color:#cbd5e1;
        }

        .dob{

            display:flex;
            gap:12px;
        }

        .btn{

            width:100%;

            padding:15px;

            border:none;

            border-radius:14px;

            background:
            linear-gradient(
                90deg,
                #2563eb,
                #3b82f6,
                #6366f1
            );

            color:white;

            font-size:16px;
            font-weight:600;

            cursor:pointer;

            margin-top:10px;

            transition:0.3s;
        }

        .btn:hover{

            transform:translateY(-2px);

            box-shadow:
            0 8px 25px rgba(59,130,246,0.4);
        }

        .result{

            margin-top:25px;

            background:rgba(255,255,255,0.05);

            border-radius:18px;

            padding:20px;

            border:1px solid rgba(255,255,255,0.08);
        }

        .student{

            text-align:center;
            margin-bottom:20px;
        }

        .student h2{

            font-size:24px;
            color:#f8fafc;
        }

        .student p{

            color:#cbd5e1;
            margin-top:5px;
        }

        .subject{

            display:flex;
            justify-content:space-between;

            padding:12px 14px;

            margin-bottom:10px;

            border-radius:12px;

            background:rgba(255,255,255,0.05);

            transition:0.3s;
        }

        .subject:hover{

            background:rgba(255,255,255,0.08);
        }

        .mark{

            font-weight:700;
            color:#60a5fa;
        }

        .footer{

            margin-top:18px;

            text-align:center;

            color:#cbd5e1;

            font-size:15px;
        }

        .badge{

            display:inline-block;

            padding:8px 14px;

            border-radius:30px;

            margin-top:10px;

            background:
            linear-gradient(
                90deg,
                #16a34a,
                #22c55e
            );

            font-size:14px;
            font-weight:600;
        }

        @media(max-width:600px){

            .container{
                padding:22px;
            }

            .title h1{
                font-size:26px;
            }

            .dob{
                flex-direction:column;
            }
        }

    </style>

</head>

<body>

<div class="bg">

    <div class="circle"></div>
    <div class="circle"></div>
    <div class="circle"></div>

</div>

<div class="container">

    <div class="title">

        <h1>TN HSE Results</h1>

        <p>Check Tamil Nadu HSE (+2) Examination Result</p>

    </div>

    <form method="POST">

        <div class="input-box">

            <label>Register Number</label>

            <input
                type="text"
                name="regno"
                placeholder="Enter Register Number"
                required
            >

        </div>

        <div class="input-box">

            <label>Date of Birth</label>

            <div class="dob">

                <select name="day" required>

                    {% for d in range(1,32) %}

                        <option value="{{'%02d' % d}}">
                            {{'%02d' % d}}
                        </option>

                    {% endfor %}

                </select>

                <select name="month" required>

                    {% for m in range(1,13) %}

                        <option value="{{'%02d' % m}}">
                            {{'%02d' % m}}
                        </option>

                    {% endfor %}

                </select>

                <select name="year" required>

                    {% for y in range(2012,1990,-1) %}

                        {% if y == 2009 %}

                            <option value="{{y}}" selected>
                                {{y}}
                            </option>

                        {% else %}

                            <option value="{{y}}">
                                {{y}}
                            </option>

                        {% endif %}

                    {% endfor %}

                </select>

            </div>

        </div>

        <button class="btn" type="submit">
            Get Result
        </button>

    </form>

    {% if result %}

        <div class="result">

            {% if result.status %}

                <div class="student">

                    <h2>{{ result.name }}</h2>

                    <p>
                        Register No:
                        {{ result.register_number }}
                    </p>

                </div>

                {% for sub in result.subjects %}

                    <div class="subject">

                        <span>{{ sub.subject }}</span>

                        <span class="mark">
                            {{ sub.mark }}
                        </span>

                    </div>

                {% endfor %}

                <div class="footer">

                    <p>
                        Total Marks:
                        <b>{{ result.total_marks }}</b>
                    </p>

                    <div class="badge">
                        {{ result.result }}
                    </div>
                    <div style="
                        margin-top:18px;
                        font-size:13px;
                        color:#94a3b8;
                    ">

                        Developed by
                        <b style="color:#60a5fa;">
                            Hari Siva
                        </b>

                </div>

            {% else %}

                <div class="footer">

                    {{ result.message }}

                </div>
                    <div style="
                        margin-top:18px;
                        font-size:13px;
                        color:#94a3b8;
                    ">

                        Developed by
                        <b style="color:#60a5fa;">
                            Hari Siva
                        </b>
            {% endif %}

        </div>

    {% endif %}

</div>

</body>
</html>

"""

# ---------------- ROUTE ----------------

@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        regno = request.form.get("regno")

        day = request.form.get("day")
        month = request.form.get("month")
        year = request.form.get("year")

        dob = f"{day}/{month}/{year}"

        result = fetch_hse_results(regno, dob)

    return render_template_string(
        HTML_PAGE,
        result=result
    )

# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


