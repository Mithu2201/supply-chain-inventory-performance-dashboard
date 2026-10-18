# Data dictionary and operational grain

**Simulation only:** no real corporate information, customer data or authenticated SAP exports. Monetary fields are in **NZD**; ISO dates use `YYYY-MM-DD` and year-month uses `YYYY-MM`.

Every processed CSV is in `data/processed/`. The matching `data/raw/` versions deliberately include controlled dirty source defects in four exports, described by `DataQualityLog.csv`.

| Table | Rows | Row grain | Primary/key | Important columns |
|---|---:|---|---|---|
| Calendar | 730 | one calendar day | `Date` | `Date`, `Year`, `MonthNumber`, `MonthName`, `Quarter`, `ISOWeek` |
| Carriers | 5 | one transport provider | `CarrierID` | `CarrierID`, `CarrierName`, `PrimaryMode`, `CostMultiplier` |
| Customers | 2,000 | one customer account | `CustomerID` | `CustomerID`, `CustomerName`, `Region`, `CustomerSegment`, `AccountReference` |
| DataQualityLog | 9 | one raw-data defect scenario | `not enforced` | `SourceTable`, `ColumnName`, `IssueType`, `AffectedRows`, `CleaningTreatment` |
| InventorySnapshots | 57,600 | one product × warehouse × month-end | `SnapshotDate+ProductID+WarehouseID` | `SnapshotDate`, `ProductID`, `WarehouseID`, `InventoryQuantity`, `InventoryValueNZD`, `SafetyStock` |
| InventoryTransactions | 164,769 | one signed movement posting (including opening balances) | `MovementID` | `MovementID`, `PostingDate`, `ProductID`, `WarehouseID`, `MovementType`, `Quantity` |
| OrderLines | 153,503 | one line of a customer sales order | `OrderLineID` | `OrderLineID`, `OrderID`, `ProductID`, `WarehouseID`, `QuantityOrdered`, `QuantityShipped` |
| Orders | 63,500 | one customer sales order | `OrderID` | `OrderID`, `OrderDate`, `RequiredDate`, `ShipDate`, `DeliveryDate`, `CustomerID` |
| PhysicalStockCounts | 12,775 | one counted product × warehouse × count event | `CountID` | `CountID`, `CountDate`, `ProductID`, `WarehouseID`, `SystemQuantity`, `PhysicalQuantity` |
| Products | 480 | one stock-keeping unit / material | `ProductID` | `ProductID`, `Material`, `MaterialDescription`, `Category`, `SupplierID`, `UnitCostNZD` |
| PurchaseOrderLines | 31,911 | one purchase order line | `POLineID` | `POLineID`, `POID`, `ProductID`, `QuantityOrdered`, `QuantityReceived`, `PurchasePriceNZD` |
| PurchaseOrders | 15,500 | one purchase-order header | `POID` | `POID`, `PODate`, `SupplierID`, `WarehouseID`, `Vendor`, `Plant` |
| SalesTargets | 120 | one calendar month × destination region | `YearMonth+Region` | `YearMonth`, `Region`, `TargetSalesNZD`, `TargetOTIF`, `TargetGrossProfitNZD` |
| Shipments | 60,438 | one dispatched order shipment | `ShipmentID` | `ShipmentID`, `OrderID`, `DeliveryNumber`, `ShipDate`, `DeliveryDate`, `RequiredDate` |
| Suppliers | 64 | one fictional supplier master | `SupplierID` | `SupplierID`, `SupplierName`, `Region`, `ContractLeadTimeDays`, `SupplierTier`, `ExpectedLateFraction` |
| TransportationCosts | 60,438 | one freight-cost record per shipment | `TransportCostID` | `TransportCostID`, `ShipmentID`, `OrderID`, `CarrierID`, `TransportMode`, `WarehouseID` |
| WarehouseLabour | 3,650 | one warehouse × workday × shift | `LabourID` | `LabourID`, `WorkDate`, `WarehouseID`, `Shift`, `LabourHours`, `LinesPicked` |
| Warehouses | 5 | one distribution warehouse | `WarehouseID` | `WarehouseID`, `WarehouseName`, `City`, `Region`, `Plant`, `StorageLocation` |

## Referential chains

`Customers -> Orders -> OrderLines -> Products -> Suppliers` represents the customer fulfilment and master-product route. `Suppliers -> PurchaseOrders -> PurchaseOrderLines -> Products` represents procurement. `Orders -> Shipments -> TransportationCosts -> Carriers` represents delivery expenses. `Warehouses + Products -> InventoryTransactions / InventorySnapshots / PhysicalStockCounts` supports stock movement and audit. `Warehouses -> WarehouseLabour` supports operating-efficiency reporting.

### SAP-style concepts (representation only)

| Extract-style field | This simulation | Similar functional process |
|---|---|---|
| Material | Products.Material (MAT000001 etc) | Material master; MM |
| Material Description | Products.MaterialDescription | Material description; MM |
| Plant | Warehouses.Plant | Plant organisation; MM/SD |
| Storage Location | Warehouses.StorageLocation | Sub-inventory by plant; MM |
| Vendor | PurchaseOrders.Vendor | Vendor/supplier references; MM |
| Purchase Order | PurchaseOrders.POID | Procurement header; MM purchasing |
| Sales Order | Orders.SalesOrder / OrderID | SD order header |
| Delivery Number | Shipments.DeliveryNumber | Outbound delivery; SD |
| Movement Type | InventoryTransactions.MovementType | 101 goods receipt; 601 goods issue; 561 opening posting |
| Posting Date | InventoryTransactions.PostingDate | Inventory accounting/posting date |
| Batch | InventoryTransactions.Batch | Material batch identifier in simulated movements |
| Goods Receipt Date | PurchaseOrderLines.GoodsReceiptDate | Received goods against an MM PO |
| Purchase Price | PurchaseOrderLines.PurchasePriceNZD | PO-line negotiated unit purchase price |

**Simplifications:** movement types use common SAP-like code semantics; there are no authentic SAP tables (MARA, EKKO, EKPO, VBAK, LIKP or MSEG/MATDOC), no actual configuration/transaction, no tax handling, no backorder replenishment workflow and no lot-level valuation. Opening movement is dated one day before the analysis period. Order sales are recorded for the shipped portion, not booked as accrued revenue on later delivery. Thus the figures demonstrate synthetic operations rather than financial statements.

## Data quality scenarios and expected treatment

| Issue | Treatment |
|---|---|
| Missing region/category | Flag as Unknown, or restore only from trusted customer/product master |
| Lower-case/padded status or description | Text.Trim / Text.Proper with controlled canonical mapping |
| Invalid OrderDate string | `try Date.FromText(_) otherwise null`, quarantine and ask for verified upstream date |
| Missing PO date | Reject from lead-time analysis until evidence is available |
| Currency symbol in numeric field | Remove "$" and parse number using specified locale |
| Blank ordered quantities | Quarantine; never invent a quantity simply to make KPIs match |
| Lower-case vendor | Normalise casing and join to supplier master |

The processed CSV files are the generator's validated canonical version, **not purportedly recovered from destroyed raw values**. The raw layer is a deliberately corrupted derivative supplied for independent Excel/Power Query/SQL cleansing exercises. To reconstruct an irrecoverable corrupted date or quantity, use a trusted original source, not guesses.

## Key assumptions

- All quantities are units in a common reporting unit; the UnitOfMeasure is descriptive only and not converted across products.
- Goods receipts are full quantity or absent, not staggered across multiple receipts.
- Stock availability at each shipment is capped at inventory available when that shipment is due to dispatch. Stock snapshots are taken from the same movement ledger.
- A shipment represents one shipped order in this simulation; financial measures must not duplicate freight by joining to several order lines.
- The baseline InventorySnapshots are **24 monthly closing balances** (2,400 SKU/warehouse points each month). Do **not** SUM inventory across months.
- `DaysSinceMovement` records elapsed days since the last 101/601 movement. It is **not lot age** or sell-through period; a warehouse receipt can reset it. Use `>90` days only as an illustrative low-activity proxy.
- `ExcessQuantity` is deliberately defined as `MAX(InventoryQuantity - 2 × ReorderPoint, 0)`; it is a teaching threshold, not an optimisation output.
- Monthly sales targets are retrospectively generated from simulated actuals with random variance for variance-analysis exercises. They are not real budgets or independent forecasts.
