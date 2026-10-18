USE SupplyChainPortfolio;
GO
-- BASIC DML MINI-LAB: real executable INSERT / UPDATE / DELETE without modifying portfolio data.
CREATE TABLE #PracticeInventory (ProductID varchar(10) PRIMARY KEY, Units int NOT NULL, Status varchar(12));
INSERT INTO #PracticeInventory(ProductID,Units,Status) VALUES ('P0001',120,'Normal'),('P0002',0,'Stockout'),('P0003',38,'Low');
SELECT * FROM #PracticeInventory ORDER BY Units ASC;
UPDATE #PracticeInventory SET Units=Units+50,Status='Replenished' WHERE ProductID='P0002';
SELECT * FROM #PracticeInventory WHERE Status='Replenished';
DELETE FROM #PracticeInventory WHERE ProductID='P0003';
SELECT * FROM #PracticeInventory;
DROP TABLE #PracticeInventory;
-- This shows SQL DML commands safely in an isolated temporary table.
-- BEGINNER: LIMIT AND FILTER
SELECT TOP (20) OrderID,OrderDate,Region,NetSalesNZD FROM dbo.Orders WHERE OrderStatus='Delivered' ORDER BY NetSalesNZD DESC;
-- INNER JOIN: line to product hierarchy
SELECT TOP (30) l.OrderLineID,p.Category,l.QuantityShipped,l.NetSalesNZD FROM dbo.OrderLines l INNER JOIN dbo.Products p ON l.ProductID=p.ProductID;
-- LEFT JOIN: retain open purchase orders with no goods receipt
SELECT TOP(20) h.POID,h.SupplierID,l.POLineID,l.GoodsReceiptDate FROM dbo.PurchaseOrders h LEFT JOIN dbo.PurchaseOrderLines l ON h.POID=l.POID WHERE l.GoodsReceiptDate IS NULL;
-- GROUP BY, HAVING
SELECT p.Category,SUM(l.NetSalesNZD) AS SalesNZD FROM dbo.OrderLines l JOIN dbo.Products p ON l.ProductID=p.ProductID GROUP BY p.Category HAVING SUM(l.NetSalesNZD)>1000000 ORDER BY SalesNZD DESC;
-- CASE: service tiers
SELECT OrderID,CASE WHEN QuantityBackordered=0 THEN 'Complete' WHEN QuantityShipped=0 THEN 'Unfilled' ELSE 'Partial' END FulfilmentClass FROM dbo.Orders;
-- CTE, aggregate, subquery
WITH RegionSales AS (SELECT Region,SUM(NetSalesNZD) Revenue FROM dbo.Orders GROUP BY Region)
SELECT Region,Revenue FROM RegionSales WHERE Revenue>(SELECT AVG(Revenue) FROM RegionSales);
-- UNION ALL (keep duplicate categories rather than implicitly de-duplicating)
SELECT 'Order units' Metric,SUM(CAST(QuantityOrdered AS bigint)) Quantity FROM dbo.OrderLines
UNION ALL SELECT 'Shipped units',SUM(CAST(QuantityShipped AS bigint)) FROM dbo.OrderLines;
-- ROW_NUMBER; product sales ranking (with deterministic tie breaker)
WITH Ranked AS (SELECT ProductID,SUM(NetSalesNZD) Sales FROM dbo.OrderLines GROUP BY ProductID)
SELECT ProductID,Sales,ROW_NUMBER() OVER(ORDER BY Sales DESC,ProductID) AS RowNo,RANK() OVER(ORDER BY Sales DESC) AS SalesRank FROM Ranked;
-- LAG/LEAD monthly trend
WITH M AS (SELECT DATEFROMPARTS(YEAR(OrderDate),MONTH(OrderDate),1) MonthStart,SUM(NetSalesNZD) Sales FROM dbo.Orders GROUP BY YEAR(OrderDate),MONTH(OrderDate))
SELECT MonthStart,Sales,LAG(Sales) OVER(ORDER BY MonthStart) PriorMonth,LEAD(Sales) OVER(ORDER BY MonthStart) NextMonth,Sales-LAG(Sales) OVER(ORDER BY MonthStart) ChangeNZD FROM M ORDER BY MonthStart;
-- SUM OVER and AVG OVER (cumulative and rolling 3 months)
WITH M AS (SELECT DATEFROMPARTS(YEAR(OrderDate),MONTH(OrderDate),1) MonthStart,SUM(NetSalesNZD) Sales FROM dbo.Orders GROUP BY YEAR(OrderDate),MONTH(OrderDate))
SELECT MonthStart,Sales,SUM(Sales) OVER(ORDER BY MonthStart ROWS UNBOUNDED PRECEDING) RunningSales,
AVG(Sales) OVER(ORDER BY MonthStart ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) Rolling3MonthAvg FROM M;
GO
-- Stored procedure: optional operational drill-through with parameterisation.
CREATE OR ALTER PROCEDURE dbo.usp_OrderExceptions @Region nvarchar(40)=NULL,@MinBackorder int=1 AS
BEGIN
 SET NOCOUNT ON;
 SELECT OrderID,OrderDate,Region,WarehouseID,QuantityBackordered,OrderStatus FROM dbo.Orders
 WHERE QuantityBackordered>=@MinBackorder AND (@Region IS NULL OR Region=@Region)
 ORDER BY QuantityBackordered DESC;
END;
GO
-- Safe DML practice in a transaction (not run against published portfolio data):
-- BEGIN TRAN; INSERT INTO dbo.Suppliers (...) VALUES (...); UPDATE ...; DELETE ...; ROLLBACK;
