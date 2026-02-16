import argparse
from pathlib import Path
import sqlite3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/buzzerbeaters.db")
    args = parser.parse_args()
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("UPDATE buzzerbeaters SET period = 'Q4' WHERE period = 'Reg'")
    updated = cur.rowcount
    conn.commit()
    conn.close()
    print(f"updated: {updated}")


if __name__ == "__main__":
    main()
