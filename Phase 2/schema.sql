-- Drop tables in reverse order of dependencies to allow clean re-execution
DROP TABLE IF EXISTS Item;
DROP TABLE IF EXISTS Invoice;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS Customer;

-- 1. Customer Table
CREATE TABLE Customer (
    Customer_ID VARCHAR(5) PRIMARY KEY,
    Country VARCHAR(100) NOT NULL
);

-- 2. Product Table
CREATE TABLE Product (
    Stock_Code VARCHAR(6) PRIMARY KEY,
    Description VARCHAR(255) NOT NULL
);

-- 3. Invoice Table
CREATE TABLE Invoice (
    Invoice_ID VARCHAR(6) PRIMARY KEY,
    Customer_ID VARCHAR(5),
    Invoice_Date DATE NOT NULL,
    CONSTRAINT fk_invoice_customer 
        FOREIGN KEY (Customer_ID) 
        REFERENCES Customer(Customer_ID) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- 4. Item Table
CREATE TABLE Item (
    Item_Code VARCHAR(6) PRIMARY KEY,
    Quantity INT NOT NULL,
    Price REAL NOT NULL DEFAULT 'GBP',
    Invoice_ID VARCHAR(6) NOT NULL,
    Stock_Code VARCHAR(6) NOT NULL,
    CONSTRAINT fk_item_invoice 
        FOREIGN KEY (Invoice_ID) 
        REFERENCES Invoice(Invoice_ID) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_item_product 
        FOREIGN KEY (Stock_Code) 
        REFERENCES Product(Stock_Code) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);