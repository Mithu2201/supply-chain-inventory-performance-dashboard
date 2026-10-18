USE SupplyChainPortfolio;
GO
-- Compare raw /data/raw and validated /data/processed; DO NOT import raw directly into typed production tables.
-- Suggested staging: dbo.RawOrders with varchar columns -> TRY_CONVERT and TRIM -> rejected_rows.
SELECT OrderID,TRIM(Region) AS CleanRegion,
CASE WHEN TRIM(LOWER(OrderStatus))='delivered' THEN 'Delivered' ELSE OrderStatus END AS CleanStatus,
TRY_CONVERT(date,OrderDate) AS ValidatedDate
FROM dbo.Orders;
-- Genuine anomaly diagnostics on CLEAN production tables:
SELECT COUNT(*) AS OrphanOrderLines FROM dbo.OrderLines l LEFT JOIN dbo.Orders h ON l.OrderID=h.OrderID WHERE h.OrderID IS NULL;
SELECT COUNT(*) AS InvalidFulfilment FROM dbo.OrderLines WHERE QuantityShipped<0 OR QuantityBackordered<0 OR QuantityShipped+QuantityBackordered<>QuantityOrdered;
SELECT COUNT(*) AS InventoryNegatives FROM dbo.InventorySnapshots WHERE InventoryQuantity<0;
SELECT COUNT(*) AS PONegativeLead FROM dbo.PurchaseOrderLines l JOIN dbo.PurchaseOrders h ON l.POID=h.POID WHERE l.GoodsReceiptDate<h.PODate;
-- UPDATE / DELETE patterns for learning: run inside a transaction and ROLLBACK by default.
BEGIN TRAN;
-- UPDATE dbo.Products SET MaterialDescription=TRIM(MaterialDescription) WHERE MaterialDescription<>TRIM(MaterialDescription);
-- DELETE FROM dbo.Products WHERE ProductID='INVALID_ID';
ROLLBACK;
GO
