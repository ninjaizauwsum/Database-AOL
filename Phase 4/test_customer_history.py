
import os
import sqlite3

folder = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(folder, "retail_database_test.db")

conn = sqlite3.connect(db_path)

try:
    # Pick a customer who has invoices.
    customer = conn.execute("""
        SELECT Customer_ID
        FROM Invoice
        WHERE Customer_ID IS NOT NULL
        LIMIT 1
    """).fetchone()

    if customer is None:
        print("No customer invoices found.")
    else:
        customer_id = customer[0]
        print(f"Invoice history for Customer ID: {customer_id}\n")

        history = conn.execute("""
            SELECT
                i.Invoice_ID,
                i.Invoice_Date,
                ROUND(SUM(it.Quantity * it.Price), 2) AS Total_Value
            FROM Invoice AS i
            JOIN Item AS it
                ON it.Invoice_ID = i.Invoice_ID
            WHERE i.Customer_ID = ?
            GROUP BY i.Invoice_ID, i.Invoice_Date
            ORDER BY i.Invoice_Date DESC
        """, (customer_id,)).fetchall()

        if history:
            print("Invoice ID | Date | Total Value")
            print("-" * 50)
            for invoice_id, date, total in history:
                print(f"{invoice_id} | {date} | {total}")

            print(f"\nPASS: Found {len(history)} invoice(s).")
        else:
            print("No invoices found for this customer.")

finally:
    conn.close()
