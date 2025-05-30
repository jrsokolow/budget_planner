# handler.py

import boto3
import csv
import os
import psycopg2
import json
from io import StringIO
from datetime import datetime
from decimal import Decimal

def parse_field(value):
    return value.strip() if value.strip() != "" else None

def to_date(val):
    val = val.strip()
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except Exception as e:
        print(f"❌ Failed to parse date '{val}': {e}")
        return None

def to_decimal(val):
    val = val.strip().replace(" ", "").replace(",", ".")
    if not val:
        return None
    try:
        return Decimal(val)
    except Exception as e:
        print(f"❌ Failed to parse decimal '{val}': {e}")
        return None

def parse_row(row):
    print(f"🔎 Parsing row: {row}")
    return [
        to_date(row[0]),
        to_date(row[1]),
        to_date(row[2]),
        to_decimal(row[3]),
        row[4] or None,
        row[5] or None,
        row[6] or None,
        row[7] or None,
        row[8] or None,
        to_decimal(row[9]),
        row[10] or None,
        row[11] or None,
        to_decimal(row[12])
    ]

def process_csv_file(csv_content, db_config):
    print("🚀 Connecting to database...")
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    csv_reader = csv.reader(StringIO(csv_content), delimiter=";")
    headers = next(csv_reader)
    print(f"🧾 CSV headers: {headers}")

    insert_sql = """
        INSERT INTO transactions (
            transaction_date, booking_date, reject_date,
            amount, currency, sender_receiver, description,
            product, transaction_type, order_amount, order_currency,
            status, balance_after
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    row_count = 0
    for row in csv_reader:
        parsed_row = parse_row(row)
        try:
            cursor.execute(insert_sql, parsed_row)
            row_count += 1
            if row_count % 50 == 0:
                print(f"📊 Inserted {row_count} rows so far...")
        except Exception as e:
            print(f"❌ Failed to insert row {row}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Finished. Inserted {row_count} rows into RDS.")

def main(event, context):
    print("🔔 Lambda triggered")

    try:
        bucket_name = os.environ["BUCKET_NAME"]
        secret_arn = os.environ["SECRET_ARN"]
        db_host = os.environ["RDS_ENDPOINT"]
        db_port = os.environ["RDS_PORT"]
        db_name = os.environ["DB_NAME"]
        print(f"🌍 Loaded environment variables: bucket={bucket_name}, db={db_name}@{db_host}:{db_port}")
    except Exception as e:
        print(f"❌ Failed to load environment variables: {e}")
        return

    try:
        s3_event = event["Records"][0]["s3"]
        object_key = s3_event["object"]["key"]
        print(f"📦 S3 event received: key={object_key}")
    except Exception as e:
        print(f"❌ Failed to parse S3 event: {e}")
        return

    try:
        s3 = boto3.client("s3")
        print("⏳ Attempting to read from S3...")
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        print("📥 CSV file read successfully from S3")
        csv_content = response["Body"].read().decode("utf-8")
        print(f"📄 CSV file read from S3, size: {len(csv_content)} bytes")
    except Exception as e:
        print(f"❌ Failed to read CSV from S3: {e}")
        return

    try:
        print("🔍 Fetching DB credentials from Secrets Manager...")
        secrets = boto3.client("secretsmanager")
        secret_value = secrets.get_secret_value(SecretId=secret_arn)
        print("🔐 Secret retrieved")
        secret_dict = json.loads(secret_value["SecretString"])
        print("🔐 Retrieved DB credentials from Secrets Manager")
    except Exception as e:
        print(f"❌ Failed to retrieve DB credentials: {e}")
        return

    db_config = {
        "host": db_host,
        "port": db_port,
        "dbname": db_name,
        "user": secret_dict["username"],
        "password": secret_dict["password"]
    }

    try:
        process_csv_file(csv_content, db_config)
    except Exception as e:
        print(f"❌ Error processing CSV file: {e}")
