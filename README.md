# Budget Planner - CSV Upload and RDS Transformation

This project consists of two parts:

- A standalone Python script to upload a CSV file to an S3 bucket
- An AWS CDK-based solution to automatically process uploaded CSV files, trigger a Lambda function, parse the data, and insert it into a PostgreSQL RDS database

---

## Requirements

- AWS CLI installed and configured
- AWS CDK installed globally (`npm install -g aws-cdk`)
- Python 3.11 installed
- Docker installed (for building Lambda layers)
- Git Bash, WSL, or compatible shell (recommended on Windows)

---

## Setup

### 1. Clone the repository

```bash
git clone <repository_url>
cd budget-csv-transform
```

### 2. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

> Ensure you have `aws-cdk-lib`, `constructs`, and `psycopg2-binary` installed locally for development.

---

## Deployment

### 1. Bootstrap AWS Environment (only once per account/region)

```bash
cdk bootstrap --profile my-profile
```

### 2. Deploy CDK Stack

```bash
cdk deploy BudgetCsvTransformStack-Test --profile my-profile
```

> **Note:** Make sure you adjust your AWS profile and region if needed.

### 3. Prepare PostgreSQL RDS table

Manually create a table in your RDS PostgreSQL instance:

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_date DATE,
    booking_date DATE,
    reject_date DATE,
    amount NUMERIC(12, 2),
    currency VARCHAR(10),
    sender_receiver TEXT,
    description TEXT,
    product TEXT,
    transaction_type TEXT,
    order_amount NUMERIC(12, 2),
    order_currency VARCHAR(10),
    status TEXT,
    balance_after NUMERIC(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

> Make sure the `budgetadmin` database user has INSERT/SELECT rights on this table and USAGE on the sequence.

---

## Using the System

### 1. Upload CSV file to S3

Use the provided standalone Python script (`uploader.py`) to upload CSV files:

```bash
python cli.py koszty.csv --bucket budget-csv-uploads-test
```

- `koszty.csv` must match the expected format (semicolon `;` delimited).
- Correct bucket name must be provided.

### 2. Lambda Trigger

Uploading a CSV automatically triggers the Lambda function:

- The Lambda reads the file from S3
- Parses and processes the data
- Inserts the records into the RDS `transactions` table

You can monitor logs via AWS CloudWatch:

- Go to **CloudWatch > Log Groups**
- Find `/aws/lambda/csv-to-rds-test`

---

## Additional Notes

- **Bucket naming**: Buckets are uniquely named based on account and region.
- **Layer deployment**: The Lambda uses a custom-built Layer containing `psycopg2` for PostgreSQL connectivity.
- **Error Handling**: Data with missing or invalid fields (dates, numerics) is safely converted to NULL.
- **Stages**: This project supports multiple environments (test/prod) via the `stage` variable.

---

## Troubleshooting

- `No module named psycopg2` → Ensure the Lambda Layer with psycopg2 is correctly deployed.
- `Bucket conflict` → Modify the bucket name to include account and region.
- `Access Denied` → Ensure correct AWS profile and permissions during deploy.

---

## Next Steps

- Add unit tests for the Lambda function.
- Build an ML model to categorize transaction data.
- Create a front-end to visualize costs and track budgets.

