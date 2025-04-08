# local_test.py

import os
from handler import process_csv_file

# Set environment variables or use hardcoded credentials
db_config = {
    "host": "localhost",
    "port": "5432",
    "dbname": "budget",
    "user": "budgetadmin",
    "password": "JvJWGgkmT5BnDj4El67H"
}

def local_main():
    with open("test.csv", encoding="utf-8") as f:
        csv_content = f.read()
        process_csv_file(csv_content, db_config)

if __name__ == "__main__":
    local_main()
