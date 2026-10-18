USE SupplyChainPortfolio;

GO

-- Source-normalised operational tables; ordered for FK dependencies.

-- Use freshly created empty DB; drop tables manually if you wish to rebuild.

IF OBJECT_ID('dbo.Warehouses','U') IS NULL
CREATE TABLE dbo.[Warehouses] (
    [WarehouseID] varchar(10),
    [WarehouseName] nvarchar(100),
    [City] nvarchar(60),
    [Region] nvarchar(40),
    [Plant] varchar(10),
    [StorageLocation] varchar(10),
    CONSTRAINT [PK_Warehouses] PRIMARY KEY ([WarehouseID])
);
GO

IF OBJECT_ID('dbo.Suppliers','U') IS NULL
CREATE TABLE dbo.[Suppliers] (
    [SupplierID] varchar(10),
    [SupplierName] nvarchar(100),
    [Region] nvarchar(40),
    [ContractLeadTimeDays] int,
    [SupplierTier] char(1),
    [ExpectedLateFraction] decimal(7,3),
    CONSTRAINT [PK_Suppliers] PRIMARY KEY ([SupplierID])
);
GO

IF OBJECT_ID('dbo.Products','U') IS NULL
CREATE TABLE dbo.[Products] (
    [ProductID] varchar(10),
    [Material] varchar(16),
    [MaterialDescription] nvarchar(100),
    [Category] nvarchar(40),
    [SupplierID] varchar(10),
    [UnitCostNZD] decimal(18,2),
    [UnitPriceNZD] decimal(18,2),
    [SafetyStock] int,
    [ReorderPoint] int,
    [LeadTimeDays] int,
    [UnitOfMeasure] varchar(10),
    CONSTRAINT [PK_Products] PRIMARY KEY ([ProductID]),
    CONSTRAINT [FK_Products_SupplierID] FOREIGN KEY ([SupplierID]) REFERENCES dbo.[Suppliers]([SupplierID])
);
GO

IF OBJECT_ID('dbo.Customers','U') IS NULL
CREATE TABLE dbo.[Customers] (
    [CustomerID] varchar(10),
    [CustomerName] nvarchar(100),
    [Region] nvarchar(40),
    [CustomerSegment] nvarchar(40),
    [AccountReference] varchar(20),
    CONSTRAINT [PK_Customers] PRIMARY KEY ([CustomerID])
);
GO

IF OBJECT_ID('dbo.Carriers','U') IS NULL
CREATE TABLE dbo.[Carriers] (
    [CarrierID] varchar(10),
    [CarrierName] nvarchar(100),
    [PrimaryMode] varchar(12),
    [CostMultiplier] decimal(8,3),
    CONSTRAINT [PK_Carriers] PRIMARY KEY ([CarrierID])
);
GO

IF OBJECT_ID('dbo.Calendar','U') IS NULL
CREATE TABLE dbo.[Calendar] (
    [Date] date,
    [Year] int,
    [MonthNumber] int,
    [MonthName] varchar(14),
    [Quarter] int,
    [ISOWeek] int,
    [NZFiscalYear] int,
    [YearMonth] char(7),
    [IsWeekday] bit,
    CONSTRAINT [PK_Calendar] PRIMARY KEY ([Date])
);
GO

IF OBJECT_ID('dbo.Orders','U') IS NULL
CREATE TABLE dbo.[Orders] (
    [OrderID] varchar(12),
    [OrderDate] date,
    [RequiredDate] date,
    [ShipDate] date NULL,
    [DeliveryDate] date NULL,
    [CustomerID] varchar(10),
    [WarehouseID] varchar(10),
    [Region] nvarchar(40),
    [OrderStatus] varchar(25),
    [QuantityOrdered] int,
    [QuantityShipped] int,
    [QuantityBackordered] int,
    [NetSalesNZD] decimal(18,2),
    [COGSNZD] decimal(18,2),
    [GrossProfitNZD] decimal(18,2),
    [SalesOrder] varchar(18) NULL,
    CONSTRAINT [PK_Orders] PRIMARY KEY ([OrderID]),
    CONSTRAINT [FK_Orders_CustomerID] FOREIGN KEY ([CustomerID]) REFERENCES dbo.[Customers]([CustomerID]),
    CONSTRAINT [FK_Orders_WarehouseID] FOREIGN KEY ([WarehouseID]) REFERENCES dbo.[Warehouses]([WarehouseID])
);
GO

IF OBJECT_ID('dbo.OrderLines','U') IS NULL
CREATE TABLE dbo.[OrderLines] (
    [OrderLineID] varchar(14),
    [OrderID] varchar(12),
    [ProductID] varchar(10),
    [WarehouseID] varchar(10),
    [QuantityOrdered] int,
    [QuantityShipped] int,
    [QuantityBackordered] int,
    [UnitPriceNZD] decimal(18,2),
    [UnitCostNZD] decimal(18,2),
    [NetSalesNZD] decimal(18,2),
    [COGSNZD] decimal(18,2),
    [GrossProfitNZD] decimal(18,2),
    [LineStatus] varchar(25),
    [Material] varchar(16),
    CONSTRAINT [PK_OrderLines] PRIMARY KEY ([OrderLineID]),
    CONSTRAINT [FK_OrderLines_OrderID] FOREIGN KEY ([OrderID]) REFERENCES dbo.[Orders]([OrderID]),
    CONSTRAINT [FK_OrderLines_ProductID] FOREIGN KEY ([ProductID]) REFERENCES dbo.[Products]([ProductID]),
    CONSTRAINT [FK_OrderLines_WarehouseID] FOREIGN KEY ([WarehouseID]) REFERENCES dbo.[Warehouses]([WarehouseID])
);
GO

IF OBJECT_ID('dbo.PurchaseOrders','U') IS NULL
CREATE TABLE dbo.[PurchaseOrders] (
    [POID] varchar(12),
    [PODate] date,
    [SupplierID] varchar(10),
    [WarehouseID] varchar(10),
    [Vendor] varchar(12),
    [Plant] varchar(10),
    [POStatus] varchar(12),
    CONSTRAINT [PK_PurchaseOrders] PRIMARY KEY ([POID]),
    CONSTRAINT [FK_PurchaseOrders_SupplierID] FOREIGN KEY ([SupplierID]) REFERENCES dbo.[Suppliers]([SupplierID]),
    CONSTRAINT [FK_PurchaseOrders_WarehouseID] FOREIGN KEY ([WarehouseID]) REFERENCES dbo.[Warehouses]([WarehouseID])
);
GO

IF OBJECT_ID('dbo.PurchaseOrderLines','U') IS NULL
CREATE TABLE dbo.[PurchaseOrderLines] (
    [POLineID] varchar(14),
    [POID] varchar(12),
    [ProductID] varchar(10),
    [QuantityOrdered] int,
    [QuantityReceived] int,
    [PurchasePriceNZD] decimal(18,2),
    [PurchaseValueNZD] decimal(18,2),
    [PromisedReceiptDate] date,
    [GoodsReceiptDate] date NULL,
    [POLineStatus] varchar(12),
    [Material] varchar(16),
    CONSTRAINT [PK_PurchaseOrderLines] PRIMARY KEY ([POLineID]),
    CONSTRAINT [FK_PurchaseOrderLines_POID] FOREIGN KEY ([POID]) REFERENCES dbo.[PurchaseOrders]([POID]),
    CONSTRAINT [FK_PurchaseOrderLines_ProductID] FOREIGN KEY ([ProductID]) REFERENCES dbo.[Products]([ProductID])
);
GO

IF OBJECT_ID('dbo.InventorySnapshots','U') IS NULL
CREATE TABLE dbo.[InventorySnapshots] (
    [SnapshotDate] date,
    [ProductID] varchar(10),
    [WarehouseID] varchar(10),
    [InventoryQuantity] int,
    [InventoryValueNZD] decimal(18,2),
    [SafetyStock] int,
    [ReorderPoint] int,
    [DaysSinceMovement] int,
    [AgeBand] varchar(8),
    [ExcessQuantity] int,
    [StockoutFlag] bit,
    [Material] varchar(16),
    [Plant] varchar(10),
    [StorageLocation] varchar(10),
    CONSTRAINT [PK_InventorySnapshots] PRIMARY KEY ([SnapshotDate], [ProductID], [WarehouseID]),
    CONSTRAINT [FK_InventorySnapshots_ProductID] FOREIGN KEY ([ProductID]) REFERENCES dbo.[Products]([ProductID]),
    CONSTRAINT [FK_InventorySnapshots_WarehouseID] FOREIGN KEY ([WarehouseID]) REFERENCES dbo.[Warehouses]([WarehouseID])
);
GO

IF OBJECT_ID('dbo.InventoryTransactions','U') IS NULL
CREATE TABLE dbo.[InventoryTransactions] (
    [MovementID] varchar(14),
    [PostingDate] date,
    [ProductID] varchar(10),
    [WarehouseID] varchar(10),
    [MovementType] varchar(3),
    [Quantity] int,
    [SignedQuantity] int,
    [ReferenceType] varchar(25),
    [ReferenceID] varchar(25),
    [Plant] varchar(10),
    [StorageLocation] varchar(10),
    [Batch] varchar(10),
    [UnitCostNZD] decimal(18,2),
    CONSTRAINT [PK_InventoryTransactions] PRIMARY KEY ([MovementID]),
    CONSTRAINT [FK_InventoryTransactions_ProductID] FOREIGN KEY ([ProductID]) REFERENCES dbo.[Products]([ProductID]),
    CONSTRAINT [FK_InventoryTransactions_WarehouseID] FOREIGN KEY ([WarehouseID]) REFERENCES dbo.[Warehouses]([WarehouseID])
);
GO

IF OBJECT_ID('dbo.Shipments','U') IS NULL
CREATE TABLE dbo.[Shipments] (
    [ShipmentID] varchar(14),
    [OrderID] varchar(12),
    [DeliveryNumber] varchar(16),
    [ShipDate] date,
    [DeliveryDate] date,
    [RequiredDate] date,
    [CarrierID] varchar(10),
    [TransportMode] varchar(12),
    [WarehouseID] varchar(10),
    [DestinationRegion] nvarchar(40),
    [UnitsShipped] int,
    [ShipmentStatus] varchar(20),
    [FreightCostNZD] decimal(18,2),
    CONSTRAINT [PK_Shipments] PRIMARY KEY ([ShipmentID]),
    CONSTRAINT [FK_Shipments_OrderID] FOREIGN KEY ([OrderID]) REFERENCES dbo.[Orders]([OrderID]),
    CONSTRAINT [FK_Shipments_CarrierID] FOREIGN KEY ([CarrierID]) REFERENCES dbo.[Carriers]([CarrierID]),
    CONSTRAINT [FK_Shipments_WarehouseID] FOREIGN KEY ([WarehouseID]) REFERENCES dbo.[Warehouses]([WarehouseID])
);
GO

IF OBJECT_ID('dbo.PhysicalStockCounts','U') IS NULL
CREATE TABLE dbo.[PhysicalStockCounts] (
    [CountID] varchar(14),
    [CountDate] date,
    [ProductID] varchar(10),
    [WarehouseID] varchar(10),
    [SystemQuantity] int,
    [PhysicalQuantity] int,
    [VarianceQuantity] int,
    [CountStatus] varchar(12),
    [Plant] varchar(10),
    CONSTRAINT [PK_PhysicalStockCounts] PRIMARY KEY ([CountID]),
    CONSTRAINT [FK_PhysicalStockCounts_ProductID] FOREIGN KEY ([ProductID]) REFERENCES dbo.[Products]([ProductID]),
    CONSTRAINT [FK_PhysicalStockCounts_WarehouseID] FOREIGN KEY ([WarehouseID]) REFERENCES dbo.[Warehouses]([WarehouseID])
);
GO

IF OBJECT_ID('dbo.WarehouseLabour','U') IS NULL
CREATE TABLE dbo.[WarehouseLabour] (
    [LabourID] varchar(14),
    [WorkDate] date,
    [WarehouseID] varchar(10),
    [Shift] varchar(12),
    [LabourHours] decimal(18,2),
    [LinesPicked] int,
    [UnitsPicked] int,
    [LabourCostNZD] decimal(18,2),
    [Plant] varchar(10),
    CONSTRAINT [PK_WarehouseLabour] PRIMARY KEY ([LabourID]),
    CONSTRAINT [FK_WarehouseLabour_WarehouseID] FOREIGN KEY ([WarehouseID]) REFERENCES dbo.[Warehouses]([WarehouseID])
);
GO

IF OBJECT_ID('dbo.TransportationCosts','U') IS NULL
CREATE TABLE dbo.[TransportationCosts] (
    [TransportCostID] varchar(14),
    [ShipmentID] varchar(14),
    [OrderID] varchar(12),
    [CarrierID] varchar(10),
    [TransportMode] varchar(12),
    [WarehouseID] varchar(10),
    [DestinationRegion] nvarchar(40),
    [CostDate] date,
    [FreightCostNZD] decimal(18,2),
    [BaseCostNZD] decimal(18,2),
    [SurchargeNZD] decimal(18,2),
    CONSTRAINT [PK_TransportationCosts] PRIMARY KEY ([TransportCostID]),
    CONSTRAINT [FK_TransportationCosts_ShipmentID] FOREIGN KEY ([ShipmentID]) REFERENCES dbo.[Shipments]([ShipmentID]),
    CONSTRAINT [FK_TransportationCosts_OrderID] FOREIGN KEY ([OrderID]) REFERENCES dbo.[Orders]([OrderID]),
    CONSTRAINT [FK_TransportationCosts_CarrierID] FOREIGN KEY ([CarrierID]) REFERENCES dbo.[Carriers]([CarrierID]),
    CONSTRAINT [FK_TransportationCosts_WarehouseID] FOREIGN KEY ([WarehouseID]) REFERENCES dbo.[Warehouses]([WarehouseID])
);
GO

IF OBJECT_ID('dbo.SalesTargets','U') IS NULL
CREATE TABLE dbo.[SalesTargets] (
    [YearMonth] char(7),
    [Region] nvarchar(40),
    [TargetSalesNZD] decimal(18,2),
    [TargetOTIF] decimal(7,3),
    [TargetGrossProfitNZD] decimal(18,2),
    CONSTRAINT [PK_SalesTargets] PRIMARY KEY ([YearMonth], [Region])
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Orders_OrderDate' AND object_id=OBJECT_ID('dbo.Orders'))
CREATE INDEX [IX_Orders_OrderDate] ON dbo.[Orders]([OrderDate]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Orders_WarehouseID' AND object_id=OBJECT_ID('dbo.Orders'))
CREATE INDEX [IX_Orders_WarehouseID] ON dbo.[Orders]([WarehouseID]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_OrderLines_ProductID' AND object_id=OBJECT_ID('dbo.OrderLines'))
CREATE INDEX [IX_OrderLines_ProductID] ON dbo.[OrderLines]([ProductID]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_OrderLines_OrderID' AND object_id=OBJECT_ID('dbo.OrderLines'))
CREATE INDEX [IX_OrderLines_OrderID] ON dbo.[OrderLines]([OrderID]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_InventorySnapshots_ProductID' AND object_id=OBJECT_ID('dbo.InventorySnapshots'))
CREATE INDEX [IX_InventorySnapshots_ProductID] ON dbo.[InventorySnapshots]([ProductID]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_InventorySnapshots_WarehouseID' AND object_id=OBJECT_ID('dbo.InventorySnapshots'))
CREATE INDEX [IX_InventorySnapshots_WarehouseID] ON dbo.[InventorySnapshots]([WarehouseID]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_PurchaseOrderLines_ProductID' AND object_id=OBJECT_ID('dbo.PurchaseOrderLines'))
CREATE INDEX [IX_PurchaseOrderLines_ProductID] ON dbo.[PurchaseOrderLines]([ProductID]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Shipments_DeliveryDate' AND object_id=OBJECT_ID('dbo.Shipments'))
CREATE INDEX [IX_Shipments_DeliveryDate] ON dbo.[Shipments]([DeliveryDate]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Shipments_CarrierID' AND object_id=OBJECT_ID('dbo.Shipments'))
CREATE INDEX [IX_Shipments_CarrierID] ON dbo.[Shipments]([CarrierID]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_PurchaseOrders_PODate' AND object_id=OBJECT_ID('dbo.PurchaseOrders'))
CREATE INDEX [IX_PurchaseOrders_PODate] ON dbo.[PurchaseOrders]([PODate]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_InventoryTransactions_PostingDate' AND object_id=OBJECT_ID('dbo.InventoryTransactions'))
CREATE INDEX [IX_InventoryTransactions_PostingDate] ON dbo.[InventoryTransactions]([PostingDate]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_WarehouseLabour_WorkDate' AND object_id=OBJECT_ID('dbo.WarehouseLabour'))
CREATE INDEX [IX_WarehouseLabour_WorkDate] ON dbo.[WarehouseLabour]([WorkDate]);
GO
