import pandas as pd
from sqlalchemy import create_engine


def csv_to_sqlite(csv_path, db_path="transactions.db", table_name="transactions"):
    df = pd.read_csv(csv_path)

    engine = create_engine(f"sqlite:///{db_path}")
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)

    print(
        f"Loaded {len(df)} rows from {csv_path} into {db_path} -> table `{table_name}`")


# usage
csv_to_sqlite("sample_data.csv")
