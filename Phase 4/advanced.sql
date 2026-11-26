

-- Add inventory, 1000 is a placeholder
ALTER TABLE Product
ADD COLUMN Stock_Level INTEGER NOT NULL DEFAULT 1000;


-- Update inventory
CREATE TRIGGER IF NOT EXISTS trg_inventory_after_insert
AFTER INSERT ON Item
FOR EACH ROW
BEGIN
    UPDATE Product
    SET Stock_Level = Stock_Level - NEW.Quantity
    WHERE Stock_Code = NEW.Stock_Code;
END;


-- Updates inventory effect
CREATE TRIGGER IF NOT EXISTS trg_inventory_after_update
AFTER UPDATE OF Quantity, Stock_Code ON Item
FOR EACH ROW
BEGIN
    -- Reverse the old item's effect
    UPDATE Product
    SET Stock_Level = Stock_Level + OLD.Quantity
    WHERE Stock_Code = OLD.Stock_Code;

    -- Apply the new item's effect
    UPDATE Product
    SET Stock_Level = Stock_Level - NEW.Quantity
    WHERE Stock_Code = NEW.Stock_Code;
END;


-- Reverse the inventory effect if an item is deleted
CREATE TRIGGER IF NOT EXISTS trg_inventory_after_delete
AFTER DELETE ON Item
FOR EACH ROW
BEGIN
    UPDATE Product
    SET Stock_Level = Stock_Level + OLD.Quantity
    WHERE Stock_Code = OLD.Stock_Code;
END;

-- Customer Invoice
SELECT
    i.Invoice_ID,
    i.Invoice_Date,
    ROUND(SUM(it.Quantity * it.Price), 2) AS Total_Value
FROM Invoice AS i
JOIN Item AS it
    ON it.Invoice_ID = i.Invoice_ID
WHERE i.Customer_ID = ?
GROUP BY i.Invoice_ID, i.Invoice_Date
ORDER BY i.Invoice_Date DESC;
