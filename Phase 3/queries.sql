-- Phase 3: Data Transactions & Queries (DML)

PRAGMA foreign_keys = ON;

CREATE INDEX IF NOT EXISTS idx_invoice_customer ON Invoice(Customer_ID);
CREATE INDEX IF NOT EXISTS idx_item_invoice ON Item(Invoice_ID);
CREATE INDEX IF NOT EXISTS idx_item_stock ON Item(Stock_Code);
CREATE INDEX IF NOT EXISTS idx_customer_country ON Customer(Country);

CREATE TABLE IF NOT EXISTS InvoiceStatus (
    Invoice_ID VARCHAR(6) PRIMARY KEY,
    Status TEXT NOT NULL DEFAULT 'Completed'
        CHECK (Status IN ('Completed', 'Cancelled')),
    FOREIGN KEY (Invoice_ID) REFERENCES Invoice(Invoice_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- QUERY 1: Price Adjustment Campaign
UPDATE Item
SET Price = ROUND(Price * 1.08, 2)
WHERE Price < 5.00;

-- QUERY 2: Order Cancellation Processing
INSERT INTO InvoiceStatus (Invoice_ID, Status)
SELECT Invoice_ID, 'Cancelled'
FROM Invoice
WHERE Invoice_ID = '489434'
ON CONFLICT(Invoice_ID)
DO UPDATE SET Status = 'Cancelled';

-- QUERY 3: Regional Sales Breakdown
SELECT
    c.Country,
    ROUND(SUM(it.Quantity * it.Price), 2) AS TotalRevenue,
    COUNT(DISTINCT i.Invoice_ID) AS CompletedInvoices
FROM Customer AS c
JOIN Invoice AS i
    ON i.Customer_ID = c.Customer_ID
JOIN Item AS it
    ON it.Invoice_ID = i.Invoice_ID
LEFT JOIN InvoiceStatus AS ist
    ON ist.Invoice_ID = i.Invoice_ID
WHERE COALESCE(ist.Status, 'Completed') = 'Completed'
GROUP BY c.Country
ORDER BY TotalRevenue DESC;

-- QUERY 4: VIP High-Spender Identification (nested query)
WITH CustomerSpending AS (
    SELECT
        c.Customer_ID,
        c.Country,
        COALESCE(SUM(
            CASE
                WHEN COALESCE(ist.Status, 'Completed') = 'Completed'
                THEN it.Quantity * it.Price
                ELSE 0
            END
        ), 0) AS TotalSpend
    FROM Customer AS c
    LEFT JOIN Invoice AS i
        ON i.Customer_ID = c.Customer_ID
    LEFT JOIN Item AS it
        ON it.Invoice_ID = i.Invoice_ID
    LEFT JOIN InvoiceStatus AS ist
        ON ist.Invoice_ID = i.Invoice_ID
    GROUP BY c.Customer_ID, c.Country
)
SELECT
    Customer_ID,
    Country,
    ROUND(TotalSpend, 2) AS TotalSpend
FROM CustomerSpending
WHERE TotalSpend > (
    SELECT AVG(TotalSpend)
    FROM CustomerSpending
)
ORDER BY TotalSpend DESC;

-- QUERY 5: Product Performance & Cross-Selling
SELECT
    p.Stock_Code,
    p.Description
FROM Product AS p
WHERE NOT EXISTS (
    SELECT 1
    FROM Item AS it
    JOIN Invoice AS i
        ON i.Invoice_ID = it.Invoice_ID
    JOIN Customer AS c
        ON c.Customer_ID = i.Customer_ID
    LEFT JOIN InvoiceStatus AS ist
        ON ist.Invoice_ID = i.Invoice_ID
    WHERE it.Stock_Code = p.Stock_Code
      AND c.Country = 'Germany'
      AND COALESCE(ist.Status, 'Completed') = 'Completed'
)
AND p.Stock_Code IN (
    SELECT it.Stock_Code
    FROM Item AS it
    JOIN Invoice AS i
        ON i.Invoice_ID = it.Invoice_ID
    JOIN Customer AS c
        ON c.Customer_ID = i.Customer_ID
    LEFT JOIN InvoiceStatus AS ist
        ON ist.Invoice_ID = i.Invoice_ID
    WHERE c.Country <> 'Germany'
      AND COALESCE(ist.Status, 'Completed') = 'Completed'
    GROUP BY it.Stock_Code
    HAVING COUNT(DISTINCT c.Country) >= 2
)
ORDER BY p.Stock_Code;
