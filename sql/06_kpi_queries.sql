USE SupplyChainPortfolio;
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
