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

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE transactions TO budgetadmin;

GRANT USAGE, SELECT ON SEQUENCE transactions_id_seq TO budgetadmin;
