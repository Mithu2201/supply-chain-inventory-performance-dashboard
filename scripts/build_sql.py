"""Creates Microsoft SQL Server DDL, CSV import, analytical views, KPI scripts."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=R/'sql'; S.mkdir(exist_ok=True)
T={
'Warehouses': [('WarehouseID','varchar(10)'),('WarehouseName','nvarchar(100)'),('City','nvarchar(60)'),('Region','nvarchar(40)'),('Plant','varchar(10)'),('StorageLocation','varchar(10)')],
'Suppliers': [('SupplierID','varchar(10)'),('SupplierName','nvarchar(100)'),('Region','nvarchar(40)'),('ContractLeadTimeDays','int'),('SupplierTier','char(1)'),('ExpectedLateFraction','decimal(7,3)')],
'Products': [('ProductID','varchar(10)'),('Material','varchar(16)'),('MaterialDescription','nvarchar(100)'),('Category','nvarchar(40)'),('SupplierID','varchar(10)'),('UnitCostNZD','decimal(18,2)'),('UnitPriceNZD','decimal(18,2)'),('SafetyStock','int'),('ReorderPoint','int'),('LeadTimeDays','int'),('UnitOfMeasure','varchar(10)')],
'Customers': [('CustomerID','varchar(10)'),('CustomerName','nvarchar(100)'),('Region','nvarchar(40)'),('CustomerSegment','nvarchar(40)'),('AccountReference','varchar(20)')],
'Carriers': [('CarrierID','varchar(10)'),('CarrierName','nvarchar(100)'),('PrimaryMode','varchar(12)'),('CostMultiplier','decimal(8,3)')],
'Calendar': [('Date','date'),('Year','int'),('MonthNumber','int'),('MonthName','varchar(14)'),('Quarter','int'),('ISOWeek','int'),('NZFiscalYear','int'),('YearMonth','char(7)'),('IsWeekday','bit')],
'Orders': [('OrderID','varchar(12)'),('OrderDate','date'),('RequiredDate','date'),('ShipDate','date NULL'),('DeliveryDate','date NULL'),('CustomerID','varchar(10)'),('WarehouseID','varchar(10)'),('Region','nvarchar(40)'),('OrderStatus','varchar(25)'),('QuantityOrdered','int'),('QuantityShipped','int'),('QuantityBackordered','int'),('NetSalesNZD','decimal(18,2)'),('COGSNZD','decimal(18,2)'),('GrossProfitNZD','decimal(18,2)'),('SalesOrder','varchar(18) NULL')],
'OrderLines': [('OrderLineID','varchar(14)'),('OrderID','varchar(12)'),('ProductID','varchar(10)'),('WarehouseID','varchar(10)'),('QuantityOrdered','int'),('QuantityShipped','int'),('QuantityBackordered','int'),('UnitPriceNZD','decimal(18,2)'),('UnitCostNZD','decimal(18,2)'),('NetSalesNZD','decimal(18,2)'),('COGSNZD','decimal(18,2)'),('GrossProfitNZD','decimal(18,2)'),('LineStatus','varchar(25)'),('Material','varchar(16)')],
'PurchaseOrders': [('POID','varchar(12)'),('PODate','date'),('SupplierID','varchar(10)'),('WarehouseID','varchar(10)'),('Vendor','varchar(12)'),('Plant','varchar(10)'),('POStatus','varchar(12)')],
'PurchaseOrderLines': [('POLineID','varchar(14)'),('POID','varchar(12)'),('ProductID','varchar(10)'),('QuantityOrdered','int'),('QuantityReceived','int'),('PurchasePriceNZD','decimal(18,2)'),('PurchaseValueNZD','decimal(18,2)'),('PromisedReceiptDate','date'),('GoodsReceiptDate','date NULL'),('POLineStatus','varchar(12)'),('Material','varchar(16)')],
'InventorySnapshots': [('SnapshotDate','date'),('ProductID','varchar(10)'),('WarehouseID','varchar(10)'),('InventoryQuantity','int'),('InventoryValueNZD','decimal(18,2)'),('SafetyStock','int'),('ReorderPoint','int'),('DaysSinceMovement','int'),('AgeBand','varchar(8)'),('ExcessQuantity','int'),('StockoutFlag','bit'),('Material','varchar(16)'),('Plant','varchar(10)'),('StorageLocation','varchar(10)')],
'InventoryTransactions': [('MovementID','varchar(14)'),('PostingDate','date'),('ProductID','varchar(10)'),('WarehouseID','varchar(10)'),('MovementType','varchar(3)'),('Quantity','int'),('SignedQuantity','int'),('ReferenceType','varchar(25)'),('ReferenceID','varchar(25)'),('Plant','varchar(10)'),('StorageLocation','varchar(10)'),('Batch','varchar(10)'),('UnitCostNZD','decimal(18,2)')],
'Shipments': [('ShipmentID','varchar(14)'),('OrderID','varchar(12)'),('DeliveryNumber','varchar(16)'),('ShipDate','date'),('DeliveryDate','date'),('RequiredDate','date'),('CarrierID','varchar(10)'),('TransportMode','varchar(12)'),('WarehouseID','varchar(10)'),('DestinationRegion','nvarchar(40)'),('UnitsShipped','int'),('ShipmentStatus','varchar(20)'),('FreightCostNZD','decimal(18,2)')],
'PhysicalStockCounts': [('CountID','varchar(14)'),('CountDate','date'),('ProductID','varchar(10)'),('WarehouseID','varchar(10)'),('SystemQuantity','int'),('PhysicalQuantity','int'),('VarianceQuantity','int'),('CountStatus','varchar(12)'),('Plant','varchar(10)')],
'WarehouseLabour': [('LabourID','varchar(14)'),('WorkDate','date'),('WarehouseID','varchar(10)'),('Shift','varchar(12)'),('LabourHours','decimal(18,2)'),('LinesPicked','int'),('UnitsPicked','int'),('LabourCostNZD','decimal(18,2)'),('Plant','varchar(10)')],
'TransportationCosts': [('TransportCostID','varchar(14)'),('ShipmentID','varchar(14)'),('OrderID','varchar(12)'),('CarrierID','varchar(10)'),('TransportMode','varchar(12)'),('WarehouseID','varchar(10)'),('DestinationRegion','nvarchar(40)'),('CostDate','date'),('FreightCostNZD','decimal(18,2)'),('BaseCostNZD','decimal(18,2)'),('SurchargeNZD','decimal(18,2)')],
'SalesTargets': [('YearMonth','char(7)'),('Region','nvarchar(40)'),('TargetSalesNZD','decimal(18,2)'),('TargetOTIF','decimal(7,3)'),('TargetGrossProfitNZD','decimal(18,2)')]
}
pk={'Warehouses':['WarehouseID'],'Suppliers':['SupplierID'],'Products':['ProductID'], 'Customers':['CustomerID'],
'Carriers':['CarrierID'],'Calendar':['Date'],'Orders':['OrderID'],'OrderLines':['OrderLineID'],
'PurchaseOrders':['POID'],'PurchaseOrderLines':['POLineID'],'InventorySnapshots':['SnapshotDate','ProductID','WarehouseID'],
'InventoryTransactions':['MovementID'],'Shipments':['ShipmentID'],'PhysicalStockCounts':['CountID'],
'WarehouseLabour':['LabourID'],'TransportationCosts':['TransportCostID'],'SalesTargets':['YearMonth','Region']}
foreign={'Products':[('SupplierID','Suppliers','SupplierID')],
'Orders':[('CustomerID','Customers','CustomerID'),('WarehouseID','Warehouses','WarehouseID')],
'OrderLines':[('OrderID','Orders','OrderID'),('ProductID','Products','ProductID'),('WarehouseID','Warehouses','WarehouseID')],
'PurchaseOrders':[('SupplierID','Suppliers','SupplierID'),('WarehouseID','Warehouses','WarehouseID')],
'PurchaseOrderLines':[('POID','PurchaseOrders','POID'),('ProductID','Products','ProductID')],
'InventorySnapshots':[('ProductID','Products','ProductID'),('WarehouseID','Warehouses','WarehouseID')],
'InventoryTransactions':[('ProductID','Products','ProductID'),('WarehouseID','Warehouses','WarehouseID')],
'Shipments':[('OrderID','Orders','OrderID'),('CarrierID','Carriers','CarrierID'),('WarehouseID','Warehouses','WarehouseID')],
'PhysicalStockCounts':[('ProductID','Products','ProductID'),('WarehouseID','Warehouses','WarehouseID')],
'WarehouseLabour':[('WarehouseID','Warehouses','WarehouseID')],
'TransportationCosts':[('ShipmentID','Shipments','ShipmentID'),('OrderID','Orders','OrderID'),('CarrierID','Carriers','CarrierID'),('WarehouseID','Warehouses','WarehouseID')]}
load_order=['Warehouses','Suppliers','Products','Customers','Carriers','Calendar','Orders','OrderLines',
'PurchaseOrders','PurchaseOrderLines','InventorySnapshots','InventoryTransactions','Shipments',
'PhysicalStockCounts','WarehouseLabour','TransportationCosts','SalesTargets']
(S/'01_create_database.sql').write_text("""-- Execute in SSMS. Creates a local portfolio database only.
IF DB_ID('SupplyChainPortfolio') IS NULL CREATE DATABASE SupplyChainPortfolio;
GO
USE SupplyChainPortfolio;
GO
""",encoding='utf-8')
lines=['USE SupplyChainPortfolio;','GO','-- Source-normalised operational tables; ordered for FK dependencies.','-- Use freshly created empty DB; drop tables manually if you wish to rebuild.']
for name in load_order:
    cols=[f'    [{col}] {ty}' for col,ty in T[name]]
    cols += ['    CONSTRAINT [PK_'+name+'] PRIMARY KEY ('+', '.join('['+c+']' for c in pk[name])+')']
    cols += [f'    CONSTRAINT [FK_{name}_{key}] FOREIGN KEY ([{key}]) REFERENCES dbo.[{ref}]([{rkey}])' for key,ref,rkey in foreign.get(name,[])]
    lines.append('IF OBJECT_ID(\'dbo.'+name+'\',\'U\') IS NULL\nCREATE TABLE dbo.['+name+'] (\n'+',\n'.join(cols)+'\n);\nGO')
for name,cols in {'Orders':['OrderDate','WarehouseID'],'OrderLines':['ProductID','OrderID'],
                  'InventorySnapshots':['ProductID','WarehouseID'],'PurchaseOrderLines':['ProductID'],
                  'Shipments':['DeliveryDate','CarrierID'],'PurchaseOrders':['PODate'],
                  'InventoryTransactions':['PostingDate'],'WarehouseLabour':['WorkDate']}.items():
    for col in cols:
        nm=f'IX_{name}_{col}'
        lines.append(f"IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='{nm}' AND object_id=OBJECT_ID('dbo.{name}'))\nCREATE INDEX [{nm}] ON dbo.[{name}]([{col}]);\nGO")
(S/'02_create_tables.sql').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')

imports=['USE SupplyChainPortfolio;\nGO',
'''-- Replace path below in EACH command using SSMS Find/Replace, or use SQLCMD variables.
-- SQL Server's service account must have read permission to this folder.
-- SQL Server 2017+ FORMAT=CSV; raw files deliberately contain corrupt values, use processed.
''']
for name in load_order:
    imports.append("BULK INSERT dbo.[%s]\nFROM 'C:\\REPLACE_WITH_YOUR_PATH\\data\\processed\\%s.csv'\nWITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);\nGO"%(name,name))
(S/'03_import_processed_csv.sql').write_text('\n'.join(imports)+'\n',encoding='utf-8')

# Star view grain: each view remains one source event grain and includes only dimensions required.
views=r'''USE SupplyChainPortfolio;
GO
-- DimDate is an existing physical table dbo.Calendar; DimRegion distinct customer/destination values.
CREATE OR ALTER VIEW dbo.DimDate AS SELECT * FROM dbo.Calendar;
GO
CREATE OR ALTER VIEW dbo.DimProduct AS SELECT ProductID,Material,MaterialDescription,Category,SupplierID,UnitCostNZD,UnitPriceNZD,SafetyStock,ReorderPoint,LeadTimeDays FROM dbo.Products;
GO
CREATE OR ALTER VIEW dbo.DimCustomer AS SELECT CustomerID,CustomerName,Region,CustomerSegment FROM dbo.Customers;
GO
CREATE OR ALTER VIEW dbo.DimSupplier AS SELECT SupplierID,SupplierName,Region,ContractLeadTimeDays,SupplierTier FROM dbo.Suppliers;
GO
CREATE OR ALTER VIEW dbo.DimWarehouse AS SELECT WarehouseID,WarehouseName,City,Region,Plant,StorageLocation FROM dbo.Warehouses;
GO
CREATE OR ALTER VIEW dbo.DimCarrier AS SELECT CarrierID,CarrierName,PrimaryMode FROM dbo.Carriers;
GO
CREATE OR ALTER VIEW dbo.DimRegion AS SELECT DISTINCT Region FROM dbo.Customers;
GO
-- Grain: order line. Monetary amounts recognised for dispatched quantities only.
CREATE OR ALTER VIEW dbo.FactOrders AS
SELECT l.OrderLineID,l.OrderID,o.OrderDate,o.RequiredDate,o.ShipDate,o.DeliveryDate,
       o.CustomerID,l.ProductID,l.WarehouseID,p.SupplierID,o.Region,o.OrderStatus,
       l.QuantityOrdered,l.QuantityShipped,l.QuantityBackordered,
       l.UnitPriceNZD,l.UnitCostNZD,l.NetSalesNZD,l.COGSNZD,l.GrossProfitNZD,l.LineStatus
FROM dbo.OrderLines l INNER JOIN dbo.Orders o ON l.OrderID=o.OrderID
INNER JOIN dbo.Products p ON l.ProductID=p.ProductID;
GO
-- Grain: product × warehouse × month-end. Semi-additive across date: use latest date.
CREATE OR ALTER VIEW dbo.FactInventory AS
SELECT SnapshotDate,ProductID,WarehouseID,InventoryQuantity,InventoryValueNZD,
       SafetyStock,ReorderPoint,DaysSinceMovement,AgeBand,ExcessQuantity,StockoutFlag
FROM dbo.InventorySnapshots;
GO
-- Grain: PO line. Lead time only for actually received lines.
CREATE OR ALTER VIEW dbo.FactPurchasing AS
SELECT l.POLineID,l.POID,h.PODate,l.PromisedReceiptDate,l.GoodsReceiptDate,
       h.SupplierID,h.WarehouseID,l.ProductID,
       l.QuantityOrdered,l.QuantityReceived,l.PurchasePriceNZD,l.PurchaseValueNZD,l.POLineStatus,
       CASE WHEN l.GoodsReceiptDate IS NOT NULL THEN DATEDIFF(day,h.PODate,l.GoodsReceiptDate) END AS ActualLeadTimeDays,
       CASE WHEN l.GoodsReceiptDate IS NOT NULL AND l.GoodsReceiptDate<=l.PromisedReceiptDate THEN 1 ELSE 0 END AS SupplierOnTimeFlag
FROM dbo.PurchaseOrderLines l INNER JOIN dbo.PurchaseOrders h ON l.POID=h.POID;
GO
-- Grain: shipment (one shipment per shipped order in this synthetic dataset).
CREATE OR ALTER VIEW dbo.FactShipments AS
SELECT s.ShipmentID,s.OrderID,s.ShipDate,s.DeliveryDate,s.RequiredDate,
       s.CarrierID,s.TransportMode,s.WarehouseID,s.DestinationRegion AS Region,
       o.CustomerID,o.QuantityOrdered,s.UnitsShipped,s.ShipmentStatus,
       s.FreightCostNZD, DATEDIFF(day,o.OrderDate,s.DeliveryDate) AS OrderCycleDays,
       CASE WHEN s.DeliveryDate<=s.RequiredDate AND s.ShipmentStatus='Delivered' THEN 1 ELSE 0 END AS OnTimeFlag,
       CASE WHEN s.UnitsShipped=o.QuantityOrdered THEN 1 ELSE 0 END AS InFullFlag
FROM dbo.Shipments s INNER JOIN dbo.Orders o ON s.OrderID=o.OrderID;
GO
-- Grain: warehouse × day × shift.
CREATE OR ALTER VIEW dbo.FactWarehouseOperations AS
SELECT LabourID,WorkDate,WarehouseID,Shift,LabourHours,LinesPicked,UnitsPicked,LabourCostNZD FROM dbo.WarehouseLabour;
GO
-- Grain: physical count occurrence.
CREATE OR ALTER VIEW dbo.FactStockCounts AS
SELECT CountID,CountDate,ProductID,WarehouseID,SystemQuantity,PhysicalQuantity,VarianceQuantity,CountStatus FROM dbo.PhysicalStockCounts;
GO
-- FactTransportCost is optional; for delivery visuals use FactShipments.FreightCostNZD rather than both tables.
CREATE OR ALTER VIEW dbo.FactTransportCost AS SELECT * FROM dbo.TransportationCosts;
GO
'''
(S/'04_build_star_views.sql').write_text(views,encoding='utf-8')
analysis=r'''USE SupplyChainPortfolio;
GO
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
'''
(S/'05_sql_learning_and_analysis.sql').write_text(analysis,encoding='utf-8')
kpi=r'''USE SupplyChainPortfolio;
GO
-- Reporting cutoff 2026-09-30. All formulas must respect the intended event grain.
-- 01: Net sales and profit, recognised on shipped lines.
SELECT SUM(NetSalesNZD) NetSalesNZD,SUM(COGSNZD) COGSNZD,SUM(GrossProfitNZD) GrossProfitNZD,
100.0*SUM(GrossProfitNZD)/NULLIF(SUM(NetSalesNZD),0) GrossMarginPct FROM dbo.OrderLines;
-- 02: OTIF at ORDER grain. Denominator: physically delivered, including partial deliveries.
SELECT COUNT(*) DeliveredOrderCount,
100.0*SUM(CASE WHEN DeliveryDate<=RequiredDate AND QuantityBackordered=0 THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0) OTIFPct,
100.0*SUM(CASE WHEN DeliveryDate<=RequiredDate THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0) OnTimePct,
100.0*SUM(CASE WHEN QuantityBackordered=0 THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0) InFullPct
FROM dbo.Orders WHERE OrderStatus IN('Delivered','Partially Delivered');
-- 03: Fill and backorder unit rates, all orders, including open orders.
SELECT SUM(CAST(QuantityBackordered AS bigint)) BackorderQty,
100.0*SUM(CAST(QuantityBackordered AS float))/NULLIF(SUM(QuantityOrdered),0) BackorderRatePct,
100.0*SUM(CAST(QuantityShipped AS float))/NULLIF(SUM(QuantityOrdered),0) FillRatePct FROM dbo.OrderLines;
-- 04: Latest snapshot inventory, not sum across all 24 snapshots.
DECLARE @AsOf date=(SELECT MAX(SnapshotDate) FROM dbo.InventorySnapshots);
SELECT @AsOf AsOfDate,SUM(InventoryValueNZD) InventoryValueNZD,
SUM(ExcessQuantity) ExcessUnits,
100.0*SUM(CAST(StockoutFlag AS float))/NULLIF(COUNT(*),0) StockoutPointPct
FROM dbo.InventorySnapshots WHERE SnapshotDate=@AsOf;
-- 05: Turnover is ANNUALISED: 2-year COGS / 2 / mean of 24 month-end inventory values.
WITH MonthValue AS (SELECT SnapshotDate,SUM(InventoryValueNZD) ValueNZD FROM dbo.InventorySnapshots GROUP BY SnapshotDate)
SELECT ((SELECT SUM(COGSNZD) FROM dbo.OrderLines)/2.0)/NULLIF(AVG(ValueNZD),0) AnnualisedInventoryTurnover,
365.0 / NULLIF(((SELECT SUM(COGSNZD) FROM dbo.OrderLines)/2.0)/NULLIF(AVG(ValueNZD),0),0) DIO_Days
FROM MonthValue;
-- 06: Physical stock exact-match accuracy. Tolerance=0 units.
SELECT 100.0*SUM(CASE WHEN SystemQuantity=PhysicalQuantity THEN 1.0 ELSE 0 END)/NULLIF(COUNT(*),0) StockCountAccuracyPct FROM dbo.PhysicalStockCounts;
-- 07: PO receipt lead time weighted at received PO-line grain.
SELECT AVG(CAST(DATEDIFF(day,h.PODate,l.GoodsReceiptDate) AS float)) AvgSupplierLeadDays,
100.0*AVG(CASE WHEN l.GoodsReceiptDate<=l.PromisedReceiptDate THEN 1.0 ELSE 0 END) SupplierOnTimePct
FROM dbo.PurchaseOrderLines l JOIN dbo.PurchaseOrders h ON l.POID=h.POID WHERE l.GoodsReceiptDate IS NOT NULL;
-- 08: Warehouse weighted productivity; exclude 'no picks' if using shift based metric alternative.
SELECT WarehouseID,SUM(UnitsPicked) UnitsPicked,SUM(LinesPicked) LinesPicked,SUM(LabourHours) LabourHours,
SUM(UnitsPicked)/NULLIF(SUM(LabourHours),0) UnitsPerLabourHour FROM dbo.WarehouseLabour GROUP BY WarehouseID;
-- 09: Transportation cost must be summed once per SHIPMENT, not once per ORDER LINE.
SELECT SUM(FreightCostNZD) TotalFreightNZD,SUM(FreightCostNZD)/NULLIF(COUNT(*),0) FreightPerShippedOrderNZD,
100.0*SUM(FreightCostNZD)/NULLIF((SELECT SUM(NetSalesNZD) FROM dbo.Orders),0) FreightPctSales FROM dbo.Shipments;
-- 10: Delivered order cycle in days; open/in-transit excluded.
SELECT AVG(CAST(DATEDIFF(day,OrderDate,DeliveryDate) AS float)) AvgOrderCycleDays FROM dbo.Orders
WHERE OrderStatus IN('Delivered','Partially Delivered');
-- 11: Customer demand-event stockout (order-line backorder occurrence).
SELECT 100.0*SUM(CASE WHEN QuantityBackordered>0 THEN 1.0 ELSE 0 END)/NULLIF(COUNT(*),0) DemandLineStockoutPct FROM dbo.OrderLines;
-- 12: latest inventory slow-moving PROXY, not FIFO lot-ageing.
SELECT Category,SUM(InventoryValueNZD) SlowInventoryNZD FROM dbo.InventorySnapshots i JOIN dbo.Products p ON i.ProductID=p.ProductID
WHERE SnapshotDate=(SELECT MAX(SnapshotDate) FROM dbo.InventorySnapshots) AND DaysSinceMovement>90 GROUP BY Category;
GO
'''
(S/'06_kpi_queries.sql').write_text(kpi,encoding='utf-8')
clean=r'''USE SupplyChainPortfolio;
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
'''
(S/'07_data_quality_and_dml_practice.sql').write_text(clean,encoding='utf-8')
print('Built',len(T),'table DDLs',len(load_order),'bulk import steps and 7 SQL scripts')
