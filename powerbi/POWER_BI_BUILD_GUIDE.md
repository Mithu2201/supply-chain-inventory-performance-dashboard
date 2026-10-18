# Power BI Desktop build guide — reproducible from SQL Server

**Status:** The SQL scripts, data model specification, measures and six data-derived design previews are supplied. **A native `.pbix` is not supplied and has not been run/tested in Power BI Desktop.** Build and save it using the steps below before showing recruiters a live report.

## 1. Prepare the SQL data

1. Install Microsoft SQL Server Developer/Express and SSMS on a Windows computer.
2. Run `sql/01_create_database.sql` and `sql/02_create_tables.sql`.
3. Edit `C:\\REPLACE_WITH_YOUR_PATH` in `sql/03_import_processed_csv.sql` to the location on the **SQL Server machine**. The SQL Server service needs read access. Run the import once on an empty database. If you see a CSV parsing error, confirm SQL Server version, access rights, locale and CSV line endings.
4. Run `sql/04_build_star_views.sql`; check results with `sql/06_kpi_queries.sql` and `documentation/validated_metrics.json`.
5. Connect Power BI Desktop: **Get data → SQL Server → Server name, Database = SupplyChainPortfolio → Import → select the `Dim*` and `Fact*` views**. Import mode is easiest for a portfolio demo. Full data refresh requires reachable SQL Server.

## 2. Recommended star relationships

Use **single direction** and **one-to-many** on dimension keys, active unless specified. Dimension keys must be unique; fact keys can repeat.

| One-side dimension | Many-side fact(s) | Key(s) |
|---|---|---|
| DimDate | FactOrders | Date → OrderDate |
| DimDate | FactInventory | Date → SnapshotDate |
| DimDate | FactPurchasing | Date → PODate |
| DimDate | FactShipments | Date → DeliveryDate |
| DimDate | FactWarehouseOperations | Date → WorkDate |
| DimDate | FactStockCounts | Date → CountDate |
| DimProduct | FactOrders, FactInventory, FactPurchasing, FactStockCounts | ProductID |
| DimCustomer | FactOrders, FactShipments | CustomerID |
| DimSupplier | FactOrders, FactPurchasing | SupplierID |
| DimWarehouse | All six operational fact views | WarehouseID |
| DimCarrier | FactShipments | CarrierID |
| DimRegion | FactOrders, FactShipments | Region |

**Caution:** `DimProduct` contains `SupplierID` as an attribute, but do not connect `DimSupplier` to `DimProduct` AND both facts; this creates ambiguous paths. Supplier filtering of inventory needs a SupplierID column in `FactInventory` or a controlled TREATAS measure. `DimRegion` represents sales destination, not warehouse origin. Supplier is not a meaningful direct filter on shipment-level carrier visuals. Use page-specific slicers rather than attempting to make every slicer affect every visual.

Set DimDate as **Mark as date table → Date**. Never join facts directly to each other, do not enable bidirectional filtering by default. SalesTargets uses `(YearMonth, Region)` grain; construct a composite dimension or bridge if using target visuals.

## 3. Add DAX measures

Create a display table `Measures` if preferred; copy one measure at a time from `Supply_Chain_DAX_Measures.dax`, set currency NZD, whole numbers and percentage formatting. Respect both denominator and event-date assumptions. **Inventory Value is semi-additive:** do not SUM all snapshot dates; use the last valid snapshot in the selected period.

## 4. Six report pages (16:9, separate page-level slicers)

| Page | Cards | Suggested visuals | Slice by |
|---|---|---|---|
| Executive | Net Sales, Gross Profit, Margin, OTIF, Inventory Value, Backorders, Freight | monthly sales line; OTIF trend; revenue by region | Date, Region |
| Inventory | Inventory Turnover, DIO, Stockout Rate, Slow-moving Value, Excess Units | category ageing; SKU-warehouse exceptions; month-end inventory trend | Date, Warehouse, Product Category |
| Supplier | Supplier Lead Time, Supplier OTIF, PO Value, late receipts | supplier rank bar, promised vs actual distribution, exception matrix | PO Date, Supplier, Warehouse |
| Warehouse | Lines/Hour, Units/Hour, Inventory Accuracy | warehouse bar, daily picking trends, count exceptions | Work Date, Warehouse |
| Transportation | Freight, Cost per Shipped Order, On-Time Delivery | carrier cost vs on-time scatter, mode, region | Delivery Date, Carrier, Region |
| Customer Orders | Sales, OTIF, Fill Rate, Backorders, Cycle Time | customer rank, regional service, backorder products | Order Date/Delivery Date, Customer, Region |

Add descriptive tooltips, bookmarks/reset filters, consistent currency and date labels, conditional formatting to matrices, accessibility contrast and alternate text. Use slicers only on related views, or display an explicit notice that a measure ignores a slicer. Use `screenshots/*_preview.png` as **layout inspiration only**; they are not native Power BI exports.

## 5. Recommended validation

For the full unfiltered time window compare `validated_metrics.json`: Net Sales NZD 198,621,923.48; Gross Profit NZD 53,843,788.85; OTIF 65.75%; Fill Rate 83.31%. Be aware of difference between (a) monthly snapshot average stockouts and (b) **latest** month-end stockout card. Also the financial annualisation is calculated over two full years only.

When complete: **File → Save As → `powerbi/Supply_Chain_Dashboard.pbix`** (not available in this download). Capture six screenshots from that real report and replace clearly-labelled preview graphics if you decide to publish actual Power BI screenshots.
