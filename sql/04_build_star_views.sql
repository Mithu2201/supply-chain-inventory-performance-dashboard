USE SupplyChainPortfolio;
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
