# 📦 CSV to S3 Uploader

A simple Python tool to upload a CSV file to an existing AWS S3 bucket.

---

## 📁 Overview

This project contains two scripts:

- `uploader.py` – contains the logic to upload a CSV file to S3.
- `cli.py` – provides a command-line interface to run the uploader with arguments.

---

## ⚙️ Requirements

- Python 3.7+
- AWS credentials (set up via `aws configure` or environment variables)
- An existing S3 bucket
- Python packages listed in `requirements.txt`

---

## 🧪 Installation

Install the required dependencies:

pip install -r requirements.txt

---

## 🚀 Usage

Run the CLI script using:

python cli.py FILE_NAME --bucket BUCKET_NAME [--object-name OBJECT_NAME]


### 🔍 Arguments

- `FILE_NAME` – Path to your local CSV file.
- `--bucket` (required) – Name of the **existing** S3 bucket.
- `--object-name` (optional) – Path (key) under which the CSV will be stored in S3.  
  If omitted, the original file name will be used.

---

### ✅ Example

```bash
python cli.py koszty.csv --bucket budget-csv-uploads-test
```

This uploads the file koszty.csv to the bucket moje-wydatki using the default object name koszty.csv.

```
python cli.py koszty.csv --bucket budget-csv-uploads-test --object-name uploads/2025-03/koszty.csv
```

This uploads the same file to the path uploads/2025-03/koszty.csv in the bucket.