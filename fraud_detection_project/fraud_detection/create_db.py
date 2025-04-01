import sqlite3

# Connect or create the DB file
conn = sqlite3.connect("transactions.db")
cursor = conn.cursor()

# Create the schema
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    amount REAL,
    nameOrig TEXT,
    nameDest TEXT,
    oldbalanceOrg REAL,
    newbalanceOrig REAL,
    oldbalanceDest REAL,
    newbalanceDest REAL,
    isFraud INTEGER
);
""")

conn.commit()
conn.close()

print("Database created: transactions.db with table `transactions`")
