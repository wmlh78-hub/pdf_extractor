from flask import Flask, render_template, request
import pdfplumber
import pandas as pd
import os
import re

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
EXCEL_FILE = os.path.join(UPLOAD_FOLDER, "output.xlsx")

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

data_list = []  # store uploaded data

# Home page
@app.route("/")
def home():
    return render_template("upload.html")

# Upload PDF
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["pdf_file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Extract data
    data = extract_data(filepath)
    data_list.append(data)

    # Save to Excel
    df = pd.DataFrame(data_list)
    df.to_excel(EXCEL_FILE, index=False)

    return f"Uploaded successfully!<br>Date: {data['date']}<br>Amount: MYR {data['amount']}"

# PDF extraction function
def extract_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # Extract amount
    amount_match = re.search(r"MYR\s?([\d,.]+)", text)
    amount = float(amount_match.group(1).replace(",", "")) if amount_match else 0

    # Extract date
    date_match = re.search(r"(\d{2}\s\w{3}\s\d{4})", text)  # example: 15 Oct 2025
    date = date_match.group(1) if date_match else "Not found"

    return {"date": date, "amount": amount}

if __name__ == "__main__":
    app.run(debug=True)
