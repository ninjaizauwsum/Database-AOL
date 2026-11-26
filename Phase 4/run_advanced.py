
import os
import re
import sqlite3

folder = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(folder, "retail_database_test.db")
sql_path = os.path.join(folder, "advanced.sql")

conn = sqlite3.connect(db_path)

try:
    # Ensure the inventory column exists.
    columns = [
        row[1] for row in conn.execute("PRAGMA table_info(Product)")
    ]

    if "Stock_Level" not in columns:
        conn.execute(
            "ALTER TABLE Product ADD COLUMN "
            "Stock_Level INTEGER NOT NULL DEFAULT 1000"
        )

    conn.execute(
        "UPDATE Product SET Stock_Level = 1000 "
        "WHERE Stock_Level IS NULL"
    )
    conn.commit()

    # The Python code above handles the column, so skip
    # the ALTER TABLE statement in advanced.sql.
    with open(sql_path, "r", encoding="utf-8") as file:
        sql = file.read()

    sql = re.sub(
        r"ALTER\s+TABLE\s+Product\s+"
        r"ADD\s+COLUMN\s+Stock_Level\s+"
        r"INTEGER\s+NOT\s+NULL\s+DEFAULT\s+1000\s*;",
        "",
        sql,
        flags=re.IGNORECASE
    )

    conn.executescript(sql)
    print("Advanced SQL triggers installed successfully.")

    # Find existing records to use for a reversible test.
    product = conn.execute(
        "SELECT Stock_Code, Stock_Level FROM Product LIMIT 1"
    ).fetchone()

    invoice = conn.execute(
        "SELECT Invoice_ID FROM Invoice LIMIT 1"
    ).fetchone()

    if product is None or invoice is None:
        print("No existing product or invoice found for testing.")
    else:
        stock_code, initial_stock = product
        invoice_id = invoice[0]

        used_codes = {
            row[0] for row in
            conn.execute("SELECT Item_Code FROM Item")
        }
        test_code = next(
            f"T{i:05d}" for i in range(100000)
            if f"T{i:05d}" not in used_codes
        )

        conn.execute("BEGIN")
        conn.execute(
            "INSERT INTO Item "
            "(Item_Code, Quantity, Price, Invoice_ID, Stock_Code) "
            "VALUES (?, ?, ?, ?, ?)",
            (test_code, 3, 1.00, invoice_id, stock_code)
        )

        new_stock = conn.execute(
            "SELECT Stock_Level FROM Product WHERE Stock_Code = ?",
            (stock_code,)
        ).fetchone()[0]

        print(f"Product: {stock_code}")
        print(f"Stock before test: {initial_stock}")
        print(f"Stock after test sale of 3: {new_stock}")

        if initial_stock - new_stock == 3:
            print("PASS: Inventory trigger works!")
        else:
            print("FAIL: Inventory did not decrease by 3.")

        # Undo the test sale and restore the database copy.
        conn.rollback()
        print("Test transaction rolled back.")

    print("\nInstalled triggers:")
    for row in conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'trigger' ORDER BY name"
    ):
        print("-", row[0])

finally:
    conn.close()
