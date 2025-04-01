import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import pytest

TEST_CSV_DATA = """type,amount,nameOrig,nameDest,oldbalanceOrg,newbalanceOrig,oldbalanceDest,newbalanceDest,isFraud
CASH_OUT,1000,C123,M123,5000,4000,1000,2000,0
TRANSFER,2000,C456,M456,1000,800,300,500,1
"""


@pytest.fixture
def temp_env(tmp_path):
    csv_path = tmp_path / "test_data.csv"
    db_path = tmp_path / "test_data.db"
    table = "transactions"

    # Write sample CSV
    with open(csv_path, "w") as f:
        f.write(TEST_CSV_DATA)

    yield {
        "csv": str(csv_path),
        "db": str(db_path),
        "table": table
    }


def create_test_db(db_path, table):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table} (
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


def load_csv_to_db(csv_file, db_file, table):
    df = pd.read_csv(csv_file)
    engine = create_engine(f"sqlite:///{db_file}")
    df.to_sql(table, con=engine, if_exists="replace", index=False)
    return df.shape[0]


def test_create_db_table(temp_env):
    create_test_db(temp_env["db"], temp_env["table"])
    conn = sqlite3.connect(temp_env["db"])
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (temp_env["table"],))
    result = cursor.fetchone()
    conn.close()
    assert result is not None, "Table creation failed."


def test_csv_data_load(temp_env):
    create_test_db(temp_env["db"], temp_env["table"])
    row_count = load_csv_to_db(
        temp_env["csv"], temp_env["db"], temp_env["table"])
    assert row_count == 2, "Expected 2 rows to load."


def test_data_content_matches(temp_env):
    create_test_db(temp_env["db"], temp_env["table"])
    load_csv_to_db(temp_env["csv"], temp_env["db"], temp_env["table"])
    engine = create_engine(f"sqlite:///{temp_env['db']}")
    df = pd.read_sql_table(temp_env["table"], con=engine)
    assert df.iloc[0]['type'] == "CASH_OUT", "First row data mismatch."
    assert df.iloc[1]['isFraud'] == 1, "Second row fraud flag mismatch."
