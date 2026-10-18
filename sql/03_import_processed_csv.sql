USE SupplyChainPortfolio;
GO
-- Replace path below in EACH command using SSMS Find/Replace, or use SQLCMD variables.
-- SQL Server's service account must have read permission to this folder.
-- SQL Server 2017+ FORMAT=CSV; raw files deliberately contain corrupt values, use processed.

BULK INSERT dbo.[Warehouses]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\Warehouses.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[Suppliers]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\Suppliers.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[Products]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\Products.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[Customers]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\Customers.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[Carriers]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\Carriers.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[Calendar]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\Calendar.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[Orders]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\Orders.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[OrderLines]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\OrderLines.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[PurchaseOrders]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\PurchaseOrders.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[PurchaseOrderLines]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\PurchaseOrderLines.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[InventorySnapshots]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\InventorySnapshots.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[InventoryTransactions]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\InventoryTransactions.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[Shipments]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\Shipments.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[PhysicalStockCounts]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\PhysicalStockCounts.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[WarehouseLabour]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\WarehouseLabour.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[TransportationCosts]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\TransportationCosts.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
BULK INSERT dbo.[SalesTargets]
FROM 'C:\REPLACE_WITH_YOUR_PATH\data\processed\SalesTargets.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK, KEEPNULLS);
GO
