import pandas as pd
import sqlite3

# this line of code is used to read the data online_retail_data(file name)
# before running don't forget to change the path
print("Loading full dataset...")
df = pd.read_csv(r"online_retail_data.csv")

# Record Original row count
original_rows = len(df)
print(f"Original CSV rows: {original_rows:,}")

# Count rows removed due to missing identifiers
before_missing = len(df)
print("Cleaning duplicates...")
#remove exact duplicates

df = df.drop_duplicates()

# used to clean datas that are missing key/critical identifiers
print("Cleaning data...")
df = df.dropna(subset=['StockCode', 'Invoice','Quantity'])

removed_missing = before_missing - len(df)

before_quantity = len(df)




#Count rows removed due to invalid quantities


cleaned_rows = len(df)

total_removed = original_rows - cleaned_rows

deletion_percentage = (
    total_removed / original_rows * 100
    if original_rows > 0 else 0
)

retention_percentage = (
    cleaned_rows / original_rows * 100
    if original_rows > 0 else 0
)

print("\n===== DATA CLEANING REPORT =====")
print(f"Original rows:         {original_rows:,}")
print(f"Removed missing IDs:   {removed_missing:,}")
print(f"Total rows deleted:    {total_removed:,}")
print(f"Rows remaining:        {cleaned_rows:,}")
print(f"Deletion percentage:   {deletion_percentage:.2f}%")
print(f"Retention percentage:  {retention_percentage:.2f}%")
print("================================\n")

# code used to standardize
df['Customer ID'] = df['Customer ID'].astype(str).str.split('.').str[0].str.zfill(5)
df['StockCode'] = df['StockCode'].astype(str)
df['Invoice'] = df['Invoice'].astype(str)
df['Quantity'] = df['Quantity'].astype(int)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate']).dt.date
df['Country'] = df['Country'].astype(str)
df['Description'] = df['Description'].astype(str)

df['Item_Code'] = "IT" + pd.RangeIndex(start=1, stop=len(df) + 1).astype(str)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

# code used to set up the database
import os

db_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "retail_database.db"
)

print("Using database:", db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# This is used to read the sql file but before running don't forget to change the path
with open("schema.sql", "r", encoding="utf-8") as f:
    cursor.executescript(f.read())

# Customer Table
customer_df = df[['Customer ID', 'Country']].drop_duplicates(subset=['Customer ID'])
customer_df.columns = ['Customer_ID', 'Country']
customer_df.to_sql('Customer', conn, if_exists='append', index=False)
print(f"Imported {len(customer_df)} customers.")

# Product Table
# handles missing descriptions
df['Description'] = (df['Description'].fillna('No desc').astype(str).str.strip())
df.loc[
    df['Description'] == '',
    'Description'
] = 'No desc'
product_df = df[['StockCode', 'Description']].drop_duplicates(subset=['StockCode'])
product_df.columns = ['Stock_Code', 'Description']
product_df.to_sql('Product', conn, if_exists='append', index=False)
print(f"Imported {len(product_df)} products.")

# Invoice Table
invoice_df = df[['Invoice', 'Customer ID', 'InvoiceDate']].drop_duplicates(subset=['Invoice'])
invoice_df.columns = ['Invoice_ID', 'Customer_ID', 'Invoice_Date']
invoice_df.to_sql('Invoice', conn, if_exists='append', index=False)
print(f"Imported {len(invoice_df)} invoices.")

# Item Table
item_df = df[['Item_Code', 'Quantity', 'Price', 'Invoice', 'StockCode']]
item_df.columns = ['Item_Code', 'Quantity', 'Price', 'Invoice_ID', 'Stock_Code']
item_df.to_sql('Item', conn, if_exists='append', index=False)
print(f"Imported {len(item_df)} line items.")

# saves and writes changes permanently to the database file
conn.commit()
# closes the file
conn.close()
# confirmation that the codes work
print("Full database import completed successfully!")