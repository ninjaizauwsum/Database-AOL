import sqlite3
import os

path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "retail_database_test.db"
)

conn = sqlite3.connect(path)

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Database:", path)
print("Tables found:")
for table in tables:
    print("-", table[0])

conn.close()