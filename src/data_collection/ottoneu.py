"""Pull Ottoneu average player values for FGPts and SABR formats."""

import os
import certifi
import duckdb
import pandas as pd
import requests

os.environ["SSL_CERT_FILE"] = certifi.where()

DB_PATH = "data/database/baseball.duckdb"

# Ottoneu format IDs
FORMATS = {
    "fgpts": 3,
    "sabr": 4,
    "classic": 1,
    "old_school": 2,
    "h2h": 5,
}


def pull_ottoneu_values(format_name: str = "fgpts") -> pd.DataFrame:
    """Download average player values from Ottoneu for a given format."""
    fmt_id = FORMATS[format_name]
    url = f"https://ottoneu.fangraphs.com/averageValues?export=csv&format={fmt_id}"
    print(f"Pulling Ottoneu {format_name} values...")
    r = requests.get(url, verify=certifi.where())
    r.raise_for_status()

    # Save raw
    raw_path = f"data/raw/ottoneu_{format_name}_values.csv"
    with open(raw_path, "wb") as f:
        f.write(r.content)

    df = pd.read_csv(raw_path)
    df["format"] = format_name
    df["snapshot_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
    print(f"  Got {len(df)} players")
    return df


def load_to_duckdb(df: pd.DataFrame, table_name: str):
    """Load a DataFrame into DuckDB."""
    con = duckdb.connect(DB_PATH)
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"  {table_name}: {count:,} rows in DuckDB")
    con.close()


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)

    for fmt in ["fgpts", "sabr"]:
        df = pull_ottoneu_values(fmt)
        load_to_duckdb(df, f"ottoneu_{fmt}_values")

    print("Done!")
