
from flask import Flask, render_template_string, request, send_file
import pandas as pd
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Face Recognition Attendance Dashboard</title>
    <style>
* {
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background: #f3f6fb;
    color: #1e293b;
    margin: 0;
    padding: 35px;
}

h1 {
    color: #173b70;
    font-size: 30px;
    margin-bottom: 30px;
}

h2 {
    color: #173b70;
}

h3 {
    color: #475569;
    font-size: 16px;
}

.card {
    display: inline-block;
    background: white;
    padding: 25px;
    margin: 0 15px 25px 0;
    min-width: 250px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.card h2 {
    font-size: 28px;
    color: #2563eb;
}

form {
    margin: 15px 0 20px;
}

input {
    padding: 11px;
    width: 260px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 14px;
}

button {
    padding: 11px 20px;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

button:hover {
    background: #173b70;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
}

th, td {
    padding: 14px;
    border: 1px solid #e2e8f0;
    text-align: left;
}

th {
    background: #173b70;
    color: white;
}

tr:nth-child(even) {
    background: #f1f5f9;
}

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
    <form action="/export" method="GET">
    <button type="submit">Download Attendance Excel</button>
</form>

<form action="/download-pdf" method="GET">
    <button type="submit">Download Attendance PDF</button>
</form>

    <form method="GET" action="/">
    <input type="text" name="search" placeholder="Search by name (Tharun or Dhanush)">
    <input type="date" name="date">
    <button type="submit">Search</button>
</form>
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

    search_name = request.args.get("search", "").strip()

    if search_name and "Name" in df.columns:
            df = df[df["Name"].astype(str).str.contains(search_name, case=False, na=False)]

    search_date = request.args.get("date", "").strip()

    if search_date and "Date" in df.columns:
            df = df[df["Date"].astype(str) == search_date]
    table = df.to_html(index=False, classes="attendance")

    return render_template_string(
        HTML, total=total, today=today, table=table
    )

@app.route("/export")
def export_attendance():
    file_path = "attendance.csv"

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="attendance.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
@app.route("/download-pdf")
def export_pdf():
    df = pd.read_csv("attendance.csv")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Attendance Report")

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, height - 90, "Name")
    pdf.drawString(220, height - 90, "Date")
    pdf.drawString(380, height - 90, "Time")

    y = height - 120
    pdf.setFont("Helvetica", 10)

    for _, row in df.iterrows():
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

        pdf.drawString(50, y, str(row["Name"]))
        pdf.drawString(220, y, str(row["Date"]))
        pdf.drawString(380, y, str(row["Time"]))
        y -= 25

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="attendance_report.pdf",
        mimetype="application/pdf"
    )
if __name__ == "__main__":
    app.run(debug=True)
    