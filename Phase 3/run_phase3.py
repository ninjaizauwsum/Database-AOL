
import sqlite3
import os

# Locate the files beside this Python script
folder = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(folder, "retail_database.db")
sql_path = os.path.join(folder, "P3 queries.sql")

# Connect to your actual database
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")

print("Database:", db_path)
print("SQL file:", sql_path)

# Read your actual Phase 3 SQL file
with open("P3 queries.sql", "r", encoding="utf-8") as file:
    sql_script = file.read()

# Split the file into individual SQL statements
statements = [
    statement.strip()
    for statement in sql_script.split(";")
    if statement.strip()
]

try:
    for number, statement in enumerate(statements, start=1):
        print(f"\n{'=' * 60}")
        print(f"STATEMENT {number}")
        print(statement)
        print("-" * 60)

        cursor = conn.execute(statement)

        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            print("Columns:", " | ".join(columns))
            print(f"Rows returned: {len(rows)}")

            for row in rows[:20]:
                print(row)

            if len(rows) > 20:
                print(f"... and {len(rows) - 20} more rows")
        else:
            print("Statement executed successfully.")
            print("Rows affected:", cursor.rowcount)

    conn.commit()
    print("\nAll SQL statements executed and committed.")

except Exception as error:
    conn.rollback()
    print("\nSQL EXECUTION FAILED")
    print(type(error).__name__ + ":", error)
    print("Changes from this run were rolled back.")

finally:
    conn.close()
