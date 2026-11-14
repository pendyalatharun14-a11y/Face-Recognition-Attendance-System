
from flask import Flask, render_template_string
import pandas as pd
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Face Recognition Attendance Dashboard</title>
    <style>
        body {
            font-family: Arial;
            background: #f2f4f8;
            margin: 30px;
        }
        h1 { color: #183153; }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: inline-block;
            min-width: 180px;
        }
        table {
            width: 100%;
            background: white;
            border-collapse: collapse;
        }
        th, td {
            padding: 14px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th { background: #183153; color: white; }
    </style>
</head>
<body>
    <h1>Face Recognition Attendance Dashboard</h1>

    <div class="card">
        <h3>Total Attendance Records</h3>
        <h2>{{ total }}</h2>
    </div>

    <div class="card">
        <h3>Today's Attendance</h3>
        <h2>{{ today }}</h2>
    </div>

    <h2>Attendance Records</h2>
    {{ table | safe }}
</body>
</html>
"""

@app.route("/")
def dashboard():
    file_path = "attendance.csv"

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])

    total = len(df)
    today_date = pd.Timestamp.now().strftime("%Y-%m-%d")

    if "Date" in df.columns:
        today = len(df[df["Date"].astype(str) == today_date])
    else:
        today = 0

    table = df.to_html(index=False, classes="attendance")

    return render_template_string(
        HTML, total=total, today=today, table=table
    )

if __name__ == "__main__":
    app.run(debug=True)
    