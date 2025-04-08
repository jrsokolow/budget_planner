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
    return datetime.strptime(val, "%Y-%m-%d").date() if val else None

def to_decimal(val):
    val = val.strip().replace(" ", "").replace(",", ".")
    return Decimal(val) if val else None

def parse_row(row):
    return [
        to_date(row[0]),       # transaction_date
        to_date(row[1]),       # booking_date
        to_date(row[2]),       # reject_date
        to_decimal(row[3]),    # amount
        row[4] or None,        # currency
        row[5] or None,        # sender_receiver
        row[6] or None,        # description
        row[7] or None,        # product
        row[8] or None,        # transaction_type
        to_decimal(row[9]),    # order_amount
        row[10] or None,       # order_currency
        row[11] or None,       # status
        to_decimal(row[12])    # balance_after
    ]

def process_csv_file(csv_content, db_config):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    csv_reader = csv.reader(StringIO(csv_content), delimiter=";")
    headers = next(csv_reader)

    insert_sql = """
        INSERT INTO transactions (
            transaction_date, booking_date, reject_date,
            amount, currency, sender_receiver, description,
            product, transaction_type, order_amount, order_currency,
            status, balance_after
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for row in csv_reader:
        parsed_row = parse_row(row)
        cursor.execute(insert_sql, parsed_row)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Data inserted into RDS")

def main(event, context):
    print("🔔 Lambda triggered")

    bucket_name = os.environ["BUCKET_NAME"]
    secret_arn = os.environ["SECRET_ARN"]
    db_host = os.environ["RDS_ENDPOINT"]
    db_port = os.environ["RDS_PORT"]
    db_name = os.environ["DB_NAME"]

    s3_event = event["Records"][0]["s3"]
    object_key = s3_event["object"]["key"]

    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    csv_content = response["Body"].read().decode("utf-8")

    secrets = boto3.client("secretsmanager")
    secret_value = secrets.get_secret_value(SecretId=secret_arn)
    secret_dict = json.loads(secret_value["SecretString"])

    db_config = {
        "host": db_host,
        "port": db_port,
        "dbname": db_name,
        "user": secret_dict["username"],
        "password": secret_dict["password"]
    }

    process_csv_file(csv_content, db_config)
