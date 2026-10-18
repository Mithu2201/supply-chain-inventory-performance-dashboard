"""Generates publishable project docs from validated summaries and CSV metadata."""
from pathlib import Path
import json,csv,collections
R=Path(__file__).resolve().parents[1]; DOC=R/'documentation';D=R/'data'/'processed';LINK=R/'linkedin'; ROOT=R
v=json.loads((DOC/'validated_metrics.json').read_text());summary=json.loads((DOC/'analysis_summary.json').read_text())
fmt=lambda v:f'{v:,.2f}'
counts={}; cols={}
for fp in sorted(D.glob('*.csv')):
    with fp.open(encoding='utf-8',newline='') as f:
        it=csv.reader(f);cols[fp.stem]=next(it)
        counts[fp.stem]=sum(1 for _ in it)
grains={
'Warehouses':'one distribution warehouse','Suppliers':'one fictional supplier master','Products':'one stock-keeping unit / material',
'Customers':'one customer account','Carriers':'one transport provider','Calendar':'one calendar day','Orders':'one customer sales order',
'OrderLines':'one line of a customer sales order','PurchaseOrders':'one purchase-order header','PurchaseOrderLines':'one purchase order line',
'InventorySnapshots':'one product × warehouse × month-end','InventoryTransactions':'one signed movement posting (including opening balances)',
'Shipments':'one dispatched order shipment','PhysicalStockCounts':'one counted product × warehouse × count event',
'WarehouseLabour':'one warehouse × workday × shift','TransportationCosts':'one freight-cost record per shipment',
'SalesTargets':'one calendar month × destination region','DataQualityLog':'one raw-data defect scenario'}
keys={'Orders':'OrderID','OrderLines':'OrderLineID','Products':'ProductID','Customers':'CustomerID','Suppliers':'SupplierID',
'PurchaseOrders':'POID','PurchaseOrderLines':'POLineID','InventorySnapshots':'SnapshotDate+ProductID+WarehouseID',
'InventoryTransactions':'MovementID','Shipments':'ShipmentID','Warehouses':'WarehouseID',
'PhysicalStockCounts':'CountID','WarehouseLabour':'LabourID','TransportationCosts':'TransportCostID',
'SalesTargets':'YearMonth+Region','Calendar':'Date','Carriers':'CarrierID','DataQualityLog':'not enforced'}
header='''# Data dictionary and operational grain

**Simulation only:** no real corporate information, customer data or authenticated SAP exports. Monetary fields are in **NZD**; ISO dates use `YYYY-MM-DD` and year-month uses `YYYY-MM`.

Every processed CSV is in `data/processed/`. The matching `data/raw/` versions deliberately include controlled dirty source defects in four exports, described by `DataQualityLog.csv`.

| Table | Rows | Row grain | Primary/key | Important columns |
|---|---:|---|---|---|
'''
for name in sorted(cols):
    colnames=', '.join(f'`{k}`' for k in cols[name][:6])
    header+=f'| {name} | {counts[name]:,} | {grains[name]} | `{keys[name]}` | {colnames} |\n'
header+='''
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
'''
(DOC/'data_dictionary.md').write_text(header,encoding='utf-8')

kpi='''# KPI definitions and safe aggregation logic

Coverage: 1 October 2024 – 30 September 2026 (two **complete** financial-analysis years, calendar date span). Shipment and PO cohorts can differ from snapshot periods. Precision and denominator choices are intentionally disclosed.

| KPI | Formula | Grain and assumption |
|---|---|---|
| Net Sales | Σ `OrderLines.NetSalesNZD` | Revenue on quantity shipped |
| Gross Profit | Net Sales − COGS | Shipped quantity × unit-cost proxy |
| Profit Margin % | Gross Profit / Net Sales | Amount-weighted |
| Inventory Value | Σ month-end `InventoryValueNZD` at ONE snapshot date | Semi-additive across months |
| Average Inventory Value | Average of 24 individual month-end totals | Only whole monthly periods |
| Annualised Inventory Turnover | `(COGS across 24 months / 2) / Average Inventory Value` | 2-year data; annualise numerator |
| Days Inventory Outstanding | `365 / annualised Inventory Turnover` | Estimated operating-finance proxy |
| Slow-Moving Inventory | Σ latest stock value with `DaysSinceMovement > 90` | Last movement proxy, **not** lot age |
| Stock Ageing % | Slow-moving Inventory / latest Inventory Value | Proxy only |
| Inventory Accuracy % | Exact-match physical count records / all physical counts | No variance tolerance |
| Snapshot Stockout Rate % | Month-end SKU/warehouse points with zero inventory / all observed SKU/warehouse points | Use single month for card; 24-month aggregate alternative |
| Demand-line Stockout Rate % | Order lines with `QuantityBackordered > 0` / all order lines | Demand-event definition, differs from snapshot rate |
| OTIF % | Delivered eligible orders both on-time and fully shipped / all eligible delivered orders | Delivered or Partially Delivered; exclude open/in-transit |
| On-Time Delivery % | Delivered eligible orders with `DeliveryDate <= RequiredDate` / eligible delivered | Order grain |
| In-Full Delivery % | Delivered eligible orders with `QuantityBackordered = 0` / eligible delivered | Order grain |
| Order Cycle Time | Average of `DeliveryDate − OrderDate` days | Eligible delivered orders |
| Supplier Lead Time | Average of `GoodsReceiptDate − PODate` | Received PO-line grain; not PO-header-weighted |
| Warehouse Productivity | Σ picked **lines** / Σ labour hours | Labour includes downtime |
| Units Picked Per Labour Hour | Σ units picked / Σ labour hours | Weighted facility-wide |
| Transportation Cost | Σ shipment-level FreightCostNZD | One shipment per dispatched order in simulation |
| Transportation Cost Per Shipped Order | Total Freight / count of all dispatched shipments | Includes in-transit; can also define delivered-only |
| Transportation Cost % of Sales | Total Freight / Net Sales | All period-shipped sales denominator |
| Backorder Quantity | Σ MAX(ordered−shipped,0) | All orders including open and partially shipped |
| Backorder Rate % | Total Backorder Units / Total Ordered Units | Unit-based, not order-event rate |
| Fill Rate % | Total Shipped Units / Total Ordered Units | Unit-based; not distinct orders |
| Supplier On-Time Delivery % | PO lines received by promised receipt date / all received PO lines | Received PO-line cohort |
| Supplier OTIF % | Received PO lines by promise date **and** in-full / all received PO lines | In this simulation, receipts are full or absent |
| Excess Inventory Units | Σ MAX(InventoryQuantity−2×ReorderPoint,0) at one snapshot | Illustrative heuristic |

## Validated global baseline

'''
for key,value in v.items():
    kpi+=f'- **{key}:** {value:,}\n' if isinstance(value,(int,float)) else f'- **{key}:** {value}\n'
kpi+='''
**Reconciliation warning:** `Stockout Rate %` on the current-period Power BI card uses **latest selected snapshot**, while `validated_metrics.json` includes **all 24 monthly snapshot observations** (`stockout_snapshot_pct`). These naturally differ. Likewise, `OTIF %` is shipment **delivery-date** filtered in Power BI but uses a full two-year delivered **order cohort** in the global Python audit: late-September orders delivered after September are not eligible for the Python global baseline.
'''
(DOC/'kpi_definitions.md').write_text(kpi,encoding='utf-8')

model='''# Logical data model and integrity design

The production layer has 17 ordinary relational source tables, physical PK/FK definitions and indexes in `sql/02_create_tables.sql`. Its Power BI star consumption layer is produced by `sql/04_build_star_views.sql`.

```mermaid
erDiagram
  DimProduct ||--o{ FactOrders : ProductID
  DimProduct ||--o{ FactInventory : ProductID
  DimProduct ||--o{ FactPurchasing : ProductID
  DimCustomer ||--o{ FactOrders : CustomerID
  DimCustomer ||--o{ FactShipments : CustomerID
  DimSupplier ||--o{ FactOrders : SupplierID
  DimSupplier ||--o{ FactPurchasing : SupplierID
  DimWarehouse ||--o{ FactOrders : WarehouseID
  DimWarehouse ||--o{ FactInventory : WarehouseID
  DimWarehouse ||--o{ FactPurchasing : WarehouseID
  DimWarehouse ||--o{ FactShipments : WarehouseID
  DimWarehouse ||--o{ FactWarehouseOperations : WarehouseID
  DimCarrier ||--o{ FactShipments : CarrierID
  DimDate ||--o{ FactOrders : OrderDate
  DimDate ||--o{ FactInventory : SnapshotDate
  DimDate ||--o{ FactPurchasing : PODate
  DimDate ||--o{ FactShipments : DeliveryDate
  DimDate ||--o{ FactWarehouseOperations : WorkDate
```

## Fact-table grain and duplication protections

| View | Record grain | Measures | Common mistake |
|---|---|---|---|
| FactOrders | One sales-order line | Sales, gross profit, shipped/backordered units | COUNTROWS as orders (counts lines instead) |
| FactInventory | One product × warehouse × month-end | Closing stock value, point stockout flags | SUM of stock across 24 months |
| FactPurchasing | One PO line | Purchase value, received lead times | Late vs not received confusion |
| FactShipments | One shipment (= one dispatched order) | Freight, on-time, in-full, cycle days | Joining one shipment with several order lines and duplicating cost |
| FactWarehouseOperations | One warehouse × day × shift | Units and lines picked, labour hours | Arithmetic average of shift productivity |
| FactStockCounts | One count event | Exact match rate | Counting missing records as correct |

A `DimDate` relationship must be one-to-many, single direction, DATE typed and marked as the date table in Power BI. Role-playing dates (OrderDate, ShipDate, DeliveryDate, PODate, GoodsReceiptDate) require disconnected role-play dimension copies or inactive relationships combined with `USERELATIONSHIP` where appropriate. Set the desired KPI event-date semantics explicitly; never filter separate facts through each other with arbitrary bidirectional relationships.

`DimRegion` means CUSTOMER DESTINATION Region for sales/shipment pages. `DimWarehouse[Region]` means ORIGIN Region. Do not make a single 'region' relationship that ambiguously mixes origins and destinations. `SalesTargets` has composite YearMonth × Region grain and must use a key bridge or TREATAS measure (not a many-to-many raw calendar month join).

## Expected cardinalities

There are 63,500 unique order headers; 153,503 distinct order-line IDs; 480 product keys; 2,000 customer keys; 64 supplier keys; 5 warehouse keys; 24 × 480 × 5 = 57,600 snapshot rows. Foreign-key references are generated from master domains rather than randomly free-typed strings.
'''
(DOC/'data_model.md').write_text(model,encoding='utf-8')

s=summary;wr=s['worst_warehouse_productivity']; slow=s['slowest_supplier'];bad=s['worst_product_backorder'];exp=s['most_expensive_carrier'];cheap=s['worst_carrier_ontime'];r=s['biggest_region_backorder'];c=s['worst_otif_region']
bi=f'''# Management insights & improvement plan (synthetic results)

**All conclusions below are exploratory interpretations of deliberately fictional operating records. No real employer, customer or external supplier performance is represented.** Metrics were computed from the full processed CSVs, not estimated from plots. Proposed impact is a test hypothesis, not a realised saving.

## Page 1 — Executive Overview

1. Sales total **NZD {fmt(v['net_sales_nzd'])}**, gross profit **NZD {fmt(v['gross_profit_nzd'])}**, gross margin **{v['gross_margin_pct']}%** over 24 months. Recommendation: protect high-margin fast movers before low-turn surplus replenishment.
2. OTIF is **{v['otif_pct']}%**, meaning more than one-third of eligible delivered orders miss the combined service requirement. Recommendation: review customer promises and item availability by date, not on-time-only metrics.
3. **{v['backorder_units']:,} units** remain backordered from an ordered demand base of {v['ordered_units']:,}, resulting in **{v['fill_rate_pct']}% unit fill rate**. Recommendation: create SKU/warehouse shortage alerts and assign replenishment owners.
4. Freight consumes **NZD {fmt(v['freight_total_nzd'])}**, around **{100*v['freight_total_nzd']/v['net_sales_nzd']:.2f}% of dispatched sales**. Recommendation: carrier-cost/service segmentation by lane before negotiating tariffs.
5. Latest closing stock is **NZD {fmt(v['latest_inventory_nzd'])}**, with a low **{v['annualised_turnover']:.2f}× annualised turnover**. Recommendation: monitor both cash tied up and service level together; avoid indiscriminate stock cuts.

## Page 2 — Inventory Performance

1. Final month closing inventory is **NZD {fmt(v['latest_inventory_nzd'])}** compared with two-year mean month-end **NZD {fmt(v['avg_month_end_inventory_nzd'])}**. Recommendation: make a stock-build bridge by receipts vs shipment issues.
2. `P0001` (Beverages) creates **{bad['BackorderUnits']:,} backordered units**, the largest individual SKU. Recommendation: examine demand distribution and reorder settings specifically at affected warehouses.
3. `P0269` ties up **NZD {fmt(s['largest_stock_value_product']['InventoryValueNZD'])}** at closing inventory. Recommendation: evaluate its stock cover, discontinue automatic ordering where holdings materially exceed the safety requirement.
4. Over the 24 month-ends, **{v['stockout_snapshot_pct']}%** of product × warehouse observation points have zero available stock; in the final month it rises to **{100*s['monthly'][-1]['StockoutPoints']/s['monthly'][-1]['InventoryPoints']:.2f}%**. Recommendation: service-focused ABC/XYZ stocking policy with different reorder rules.
5. **NZD {fmt(sum(x['SlowInventoryNZD'] for x in s['products']))}** meets the strict 90+ days-since-last-movement proxy at final snapshot. A receipt resets this timer; this **understates possible FIFO-aged on-hand stock**. Recommendation: gather lot receipt dates for genuine inventory-age analysis.

## Page 3 — Supplier Performance

1. Mean completed PO-line lead time is **{v['mean_supplier_receipt_lead_days']} days**. Recommendation: segment vendor promises and actual performance using line-level receipt dates.
2. `SUP052` averages **{slow['AvgLeadTimeDays']} days** among {slow['ReceivedLines']} received lines, with **{slow['OnTimeReceiptPct']}% recorded on-time**. Recommendation: test contract feasibility and order-release timing; do not assume the data identifies causation.
3. `SUP039` has the highest simulated total PO-line purchase value at around **NZD {fmt(max(s['suppliers'], key=lambda x:x['PurchaseValueNZD'])['PurchaseValueNZD'])}**. Recommendation: focus supplier review on both spend concentration and service reliability.
4. Several suppliers have 0% on-time receipts in the simulation despite completed receipts. Recommendation: check promise-date quality and agreed buffers before supplier sanctions.
5. Open PO lines are excluded from completed lead-time averages. Recommendation: add a separate overdue-open PO report so the lead-time metric does not hide non-receipt risk.

## Page 4 — Warehouse Performance

1. `WH03` averages **{wr['UnitsPerLabourHour']} units per labour hour**, the lowest observed site, compared with `WH01` at **{next(x for x in s['warehouses'] if x['WarehouseID']=='WH01')['UnitsPerLabourHour']}**. Recommendation: measure travel paths, pick density and wave-planning process, adjusting for product mix.
2. All warehouses together processed **{v['picked_units']:,} units** using **{fmt(v['labour_hours'])} labour hours**. Recommendation: use weighted output/hours, not the mean of daily ratios.
3. Global exact-match physical stock count accuracy is **{v['inventory_accuracy_pct']}%**. Recommendation: cycle counts prioritised by high-value discrepancies and repeated variance SKUs.
4. `WH04` has the weakest site stock-record accuracy in the simulation at **{next(x for x in s['warehouses'] if x['WarehouseID']=='WH04')['InventoryAccuracyPct']}%**. Recommendation: audit movement discipline, recording timing, bin transfers and picking exceptions.
5. Labour hours include inactive periods, so units/hour measures overall shift efficiency rather than individual worker performance. Recommendation: add labour job codes before attributing the gap to staff.

## Page 5 — Transportation Performance

1. `CR04` averages **NZD {exp['CostPerShipmentNZD']} per shipment** with **{exp['OnTimePct']}% on-time delivered service**. Recommendation: reserve this premium service for urgent/high-value lanes, subject to volume and route mix controls.
2. `CR03` averages **NZD {cheap['CostPerShipmentNZD']} per shipment**, but its on-time result is only **{cheap['OnTimePct']}%**. Recommendation: analyse service improvement potential and customer penalty costs before selecting solely on price.
3. In total, freight expense is **NZD {fmt(v['freight_total_nzd'])}**, roughly **NZD {v['freight_total_nzd']/len([x for x in s['monthly']]):,.0f} per month**. Recommendation: monitor lane- and carrier-normalised cost per shipment.
4. Cost-per-order uses shipped orders (there is one shipment/order here); a future split-delivery system will require distinct order counts. Recommendation: preserve shipment and order keys separately in the data model.
5. Carrier comparison is descriptive, not causal; distances, volumes and urgency vary. Recommendation: run like-for-like lane analyses before signing new contracts.

## Page 6 — Customer and Order Performance

1. `Canterbury` has the lowest measured regional delivered-order OTIF at **{c['OTIFPct']}%**. Recommendation: focus root-cause exception codes, rather than blanket delivery promises.
2. `Wellington` has the highest cumulative backorders: **{r['BackorderUnits']:,} units**. Recommendation: isolate category/SKU concentration before allocating stock transfers.
3. `Wellington` also produces the greatest sales of the five destination regions: **NZD {fmt(r['NetSalesNZD'])}**. Recommendation: evaluate fill-rate improvement in proportion to region demand and customer priority.
4. The combined unit fill rate of **{v['fill_rate_pct']}%** is not interchangeable with **{v['otif_pct']}% OTIF**; one is item-unit based and one is delivered-order event based. Recommendation: report both service perspectives.
5. Exclude open and in-transit orders from delivered-order OTIF, but keep them visible on a separate exception backlog card. Recommendation: track ageing of outstanding promises weekly.

## Prioritised 30/60/90-day action roadmap

| Window | Hypothesis-led action | Measure of success (proposed target, not generated result) |
|---|---|---|
| 0–30 days | Review P0001/P0003 shortage patterns and audit WH04 stock variance | Identify top 20 exception SKUs and variance causes |
| 0–30 days | Validate SUP052/SUP039 promised vs receipt dates | Agreed root-cause tags per received/overdue PO line |
| 31–60 days | Trial adjusted reorder settings on selected fast movers | Lower demand-line stockout without growing surplus |
| 31–60 days | Pilot pick-path review at WH03 | Improve comparable throughput with quality held constant |
| 61–90 days | Carrier service-cost lane review | Improve OTIF per freight NZD on matched lanes |
| 61–90 days | Implement executive weekly exception review | Report OTIF, overdue POs, backorder ageing and cash tied in stock together |
'''
(DOC/'business_insights.md').write_text(bi,encoding='utf-8')

quality='''# Data cleaning lab — audit, repair and review

Run Power Query against `data/raw/`, NOT `data/processed/`, and build a reproducible transformation pipeline. Canonical cleaned files are provided as an **independent reference output** generated before intentional corruption.

## Recommended exercise

1. Import raw Orders into Power Query as text, promote headers, type OrderDate with `try … otherwise null`, preserve an InvalidDate flag.
2. Apply Trim and Clean to status and descriptions; map known statuses only (`Delivered`, `Partially Delivered`, `In Transit`, `Open`). Do not quietly treat unknown statuses as Delivered.
3. Replace missing Region from Customers on CustomerID, but label unresolved rows as Unknown and audit how many.
4. Import Products, mark blank Category and reconcile using a trusted master.
5. Convert currency text in raw OrderLines by stripping `$` and parsing to Decimal; quarantine blank numeric quantities. Check `QuantityOrdered = QuantityShipped + QuantityBackordered` only after successful recovery.
6. On PurchaseOrders, vendor casing can be canonicalised; missing PO dates must be rejected from lead-time calculations pending an approved source.
7. Create rejected-record and repaired-record counts; compare KPI totals to `documentation/validated_metrics.json`. Preserve an audit log describing the source of each repair.

`DataQualityLog.csv` records nine intentionally injected issue types. `powerbi/PowerQuery_Raw_Orders_Cleanup.pq` includes a working example of flagging rather than silently fabricating invalid dates.

## SQL quality queries

See `sql/07_data_quality_and_dml_practice.sql` for FK, arithmetic and ledger diagnostics. SQL creation scripts load processed files to preserve FK consistency; an advanced follow-on exercise is to create all-VARCHAR staging tables for raw and use `TRY_CONVERT` to split accepted rows from rejected rows.
'''
(DOC/'data_cleaning_playbook.md').write_text(quality,encoding='utf-8')

README=f'''# End-to-End Supply Chain & Inventory Performance Dashboard

![Executive Overview (data-derived design preview, not Power BI screenshot)](screenshots/executive_dashboard_preview.png)

**Professional portfolio case study | New Zealand distribution scenario | 1 Oct 2024–30 Sep 2026**

> **Fictional, reproducible case study.** All customers, suppliers, material masters, plant codes, logistics results and financial metrics are **synthetic**. SAP-style fields are teaching analogues, not data extracted from any SAP environment. Report PNG files are **data-driven visual concepts**, not exported `.pbix` screenshots. A native Power BI project must be built following `powerbi/POWER_BI_BUILD_GUIDE.md`.

## Project overview

Design a realistic end-to-end supply chain, sales fulfilment, warehouse and inventory analytics solution demonstrating practical **Excel → SQL Server → Power BI** reporting, operations research and management improvement skills.

### Headline metrics (two-year simulated baseline)

| Measure | Audited result |
|---|---:|
| Sales orders | {v['orders']:,} |
| Order lines | {v['order_lines']:,} |
| Products / customers / suppliers / warehouses | {v['products']:,} / 2,000 / 64 / 5 |
| Net sales | NZD {fmt(v['net_sales_nzd'])} |
| Gross profit | NZD {fmt(v['gross_profit_nzd'])} |
| Gross profit margin | {v['gross_margin_pct']}% |
| Delivered-order OTIF | {v['otif_pct']}% |
| Unit fill rate | {v['fill_rate_pct']}% |
| Backordered units | {v['backorder_units']:,} |
| Latest inventory valuation | NZD {fmt(v['latest_inventory_nzd'])} |
| Annualised inventory turnover | {v['annualised_turnover']:.2f}× |
| Physical-stock exact match | {v['inventory_accuracy_pct']}% |
| Transportation cost | NZD {fmt(v['freight_total_nzd'])} |

## Business problem and objectives

A fictional multi-region wholesale distributor struggles with (1) inventory shortages on popular products, (2) inventory funding pressure due to surplus stock, (3) differing supplier lead times, (4) warehouse throughput differences, (5) customer OTIF misses and (6) transport-cost/service tradeoffs. The analytical objectives are to define reliable KPIs, build a model that preserves **event grain**, identify exceptions and propose data-driven improvement experiments.

## Tools and skills

- **Microsoft Excel:** structured tables, KPI analysis, lookup exercises, PivotTable/slicer guide, conditional formatting and Power Query cleaning exercises.
- **SQL Server:** 17 typed relational source tables, PK/FK/indexes, CSV BULK INSERT, analytical views, beginner-to-advanced SQL, CTEs, window functions, KPI queries and stored procedure.
- **Power BI / DAX:** multi-fact star model, 30+ measures, date intelligence assumptions, 6-page visual blueprint, guidance to build a `.pbix` in Power BI Desktop.
- **SAP-style processes:** MM purchasing, material/plant/storage-location organisation, SD order/delivery concepts and movement types 101/601/561.
- **Operations and business analysis:** inventory valuation, service levels, supplier performance, warehouse throughput, transport cost and operational recommendations.

## Dataset & architecture

The generator `scripts/generate_dataset.py` creates deterministic, cross-linked transactional records using a fixed random seed (NumPy required). `data/raw/` is deliberately dirty on selected fields; `data/processed/` is canonical validated data. Inventory balances come from opening balances, actual simulated purchase receipts and capped dispatch issues. Two years of month-end snapshots are recorded. See [Data Dictionary](documentation/data_dictionary.md).

```text
Fictional system extracts (CSV) -- Power Query cleaning lab
           |                                |
      data/raw/                       data/processed/
                                            |
                                    SQL Server (17 tables)
                                            |
                                      Fact/Dim SQL views
                                            |
                                Power BI import + DAX model
                                            |
                                 Six-page report (build guide)
```

## Analytics / data cleaning

Run [data-cleaning lab](documentation/data_cleaning_playbook.md). Reconciliation checks enforce IDs, unit accounting, nonnegative inventory and signed goods movements. Never claim that the generator's validated output was independently recovered from intentionally destroyed source values.

## SQL analysis and Power BI model

In SSMS run scripts in numeric order: `01_create_database`, `02_create_tables`, `03_import_processed_csv`, `04_build_star_views`, `05_sql_learning_and_analysis`, `06_kpi_queries`, `07_data_quality_and_dml_practice` (last two can be run independently for learning). Read [Data Model](documentation/data_model.md), [KPI Definitions](documentation/kpi_definitions.md) and [Power BI build guide](powerbi/POWER_BI_BUILD_GUIDE.md). **The SQL Server BULK INSERT absolute file path must be edited first.**

DAX measures live in [Supply_Chain_DAX_Measures.dax](powerbi/Supply_Chain_DAX_Measures.dax); Power Query example is in [PowerQuery_Raw_Orders_Cleanup.pq](powerbi/PowerQuery_Raw_Orders_Cleanup.pq). Currency is NZD and percentage calculations return 0–1 in DAX.

## Excel workbook

Open [Supply_Chain_Analysis.xlsx](excel/Supply_Chain_Analysis.xlsx) and begin at `START_HERE` and `Excel_Analysis`. Prebuilt formula-driven KPI blocks link to complete aggregate tables. A 450-order sample and 300-line sample support lookup/date exercises; **the full calculations use all 153,503 order lines via summary CSVs**, not the samples. Excel PivotTables/PivotCharts/Slicers require you to insert them in desktop Excel following `Excel_Methods` instructions, and are not supplied as native PivotTable objects.

## Dashboard page specifications

1. **Executive Overview:** net sales, gross profit, OTIF, inventory, backorders, freight and time series.
2. **Inventory Performance:** turnover, inventory valuation, stockout points, excess and slow-moving stock.
3. **Supplier Performance:** actual vs promised lead time, PO spend, on-time receipts, ranks.
4. **Warehouse Performance:** picking output, hours, units/hour and stock accuracy.
5. **Transportation Performance:** cost, carriers, region, mode and on-time tradeoffs.
6. **Customer & Order Performance:** OTIF, fill rate, customer/region sales and backorder exceptions.

![Inventory design preview](screenshots/inventory_dashboard_preview.png)
![Supplier design preview](screenshots/supplier_dashboard_preview.png)
![Warehouse design preview](screenshots/warehouse_dashboard_preview.png)
![Transportation design preview](screenshots/transportation_dashboard_preview.png)
![Customer and order design preview](screenshots/customer_orders_dashboard_preview.png)

## Actual findings from simulated data

- `P0001` has **{s['worst_product_backorder']['BackorderUnits']:,} backordered units** — a targeted replenishment candidate.
- `SUP052` averages **{s['slowest_supplier']['AvgLeadTimeDays']} days** to receipt among completed PO lines.
- Warehouse `WH03` is lowest at **{s['worst_warehouse_productivity']['UnitsPerLabourHour']} units/hour** — investigate comparable labour processes.
- Carrier `CR03` has lower typical cost, but **{s['worst_carrier_ontime']['OnTimePct']}% on-time service**, while premium `CR04` is costly and more reliable.
- `Canterbury` has the lowest regional **{s['worst_otif_region']['OTIFPct']}%** delivered-order OTIF; `Wellington` has the largest total backorders.

Each report page includes at least five grounded management findings and a practical action proposal in [Business Insights](documentation/business_insights.md). These are simulated observations and hypotheses, not claims about actual organisations.

## Getting started / reproduce project

```powershell
# 1. Clone a public repository after uploading these project files
# git clone https://github.com/YOUR-USERNAME/supply-chain-inventory-performance-dashboard.git
cd supply-chain-inventory-performance-dashboard

# 2. (Optional) regenerate source data — Python 3.10+ and NumPy
python -m pip install numpy matplotlib
python scripts/generate_dataset.py
python scripts/build_sql.py
python scripts/build_reporting_assets.py
# Build the workbook with artifact_tool in a compatible Python environment:
python scripts/build_excel.py
```

Artifacts are included already; regeneration is optional. Note that the `artifact_tool` Python library used to build the Excel workbook may not be installed in all local environments, but the distributed `.xlsx` can be opened in ordinary Microsoft Excel.

## Project structure

```text
supply-chain-inventory-performance-dashboard/
├── README.md
├── data/
│   ├── raw/                         # source-like deliberate defects
│   └── processed/                   # 17 validated source CSVs + quality log
├── excel/
│   ├── Supply_Chain_Analysis.xlsx
│   └── *_Summary.csv               # source tables for Excel KPI exercises
├── sql/
│   └── 01–07_*.sql
├── powerbi/
│   ├── Supply_Chain_DAX_Measures.dax
│   ├── PowerQuery_Raw_Orders_Cleanup.pq
│   └── POWER_BI_BUILD_GUIDE.md
├── screenshots/
│   └── six *_preview.png graphics  # NOT real Power BI screenshots
├── scripts/
│   └── reproducible Python build scripts
├── documentation/
│   ├── data_dictionary.md
│   ├── kpi_definitions.md
│   ├── data_model.md
│   ├── data_cleaning_playbook.md
│   ├── business_insights.md
│   ├── validated_metrics.json
│   └── analysis_summary.json
└── linkedin/
    └── profile_kit.md
```

## Publishing and attribution

See [GitHub upload instructions](documentation/github_upload_guide.md) and [LinkedIn / CV kit](linkedin/profile_kit.md). All names and figures are fictional. Avoid suggesting enterprise SAP or a production Power BI deployment was performed. Add your actual `.pbix` only after building it in Power BI Desktop.

## Skills demonstrated

Supply Chain & Logistics Analytics • Inventory Analysis • Procurement and Supplier Analysis • Warehouse Operations • Transportation Analysis • Advanced Excel • SQL Server • Power Query • Power BI modelling and DAX design • Data Cleaning • Star Schema • SAP-style Operational Data • KPI Design • Exception Reporting • Operational Improvement • Business Insights • Reproducible Python Simulation
'''
(ROOT/'README.md').write_text(README,encoding='utf-8')

github='''# Upload the portfolio project to GitHub

The folder in this ZIP **is not itself a live GitHub repository**. You need a GitHub account and must create and push the repo.

## Recommended approach — Git command line

1. Extract the ZIP somewhere on Windows. Install Git for Windows and open PowerShell or Git Bash.
2. On github.com select **New repository**, set its name to `supply-chain-inventory-performance-dashboard`, choose Public and **do not initialise** it with another README/.gitignore (this ZIP already includes README).
3. In terminal, inside the extracted project folder:

```powershell
git init
git add .
git commit -m "Add synthetic NZ supply-chain and inventory analytics portfolio"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/supply-chain-inventory-performance-dashboard.git
git push -u origin main
```

Authentication may open a browser. Substitute YOUR-USERNAME. If Git asks for identity, configure `git config --global user.name` and `user.email` first. GitHub does not normally accept an account password directly for command-line HTTPS pushes; use the prompted supported sign-in or appropriate credential method.

## Alternative — GitHub web upload

Create an empty public repository and choose **Add file → Upload files**. For this many files, the Git command line or GitHub Desktop is more reliable than uploading files individually. Keep the directory hierarchy, not a single zipped blob if you want GitHub to display the README and SQL scripts.

## Post-upload checks

- README images display and links to markdown docs work.
- `data/processed/OrderLines.csv` has 153,503 body rows (approx 14 MB) and no single CSV exceeds GitHub's 100 MB hard file limit.
- `.xlsx`, 7 `.sql` scripts, DAX measures and six concept previews exist.
- Never call the concept previews actual Power BI screenshots or claim `.pbix` was delivered.
- Add your finished `.pbix` after creating and validating it in Microsoft Power BI Desktop; update its status in README.

## Add to LinkedIn

Open your LinkedIn profile, find **Add profile section → Recommended → Add featured** (the layout may change), select **Add link**, paste your public GitHub repo URL, and set a project title and short description. Alternatively add it in **Projects** in Accomplishments if your profile offers that section. Paste the prepared public announcement from `linkedin/profile_kit.md`, with your *actual verified URL*.
'''
(DOC/'github_upload_guide.md').write_text(github,encoding='utf-8')

linkedin='''# LinkedIn, CV and recruiter communication kit

Replace `YOUR-USERNAME` with your actual GitHub handle **after pushing** the repository. Never claim that the native Power BI `.pbix` exists until you build and save it.

## Featured section project description

**End-to-End Supply Chain & Inventory Performance Dashboard | Synthetic NZ Operations Case Study**

Designed a reproducible two-year distribution analytics case using 153,503 order lines, SQL Server relational tables, advanced Excel analysis, SAP-style procurement/inventory extracts and a multi-page Power BI model and DAX measure blueprint. Investigated fulfilment reliability, stockouts, inventory turnover, supplier lead times, warehouse picking and transport cost. Documented business improvement proposals, data-quality controls and validated operational KPIs. Synthetic dataset; report previews are visual concepts.

**Repository:** https://github.com/YOUR-USERNAME/supply-chain-inventory-performance-dashboard

## Suggested LinkedIn post (accurate to the delivered package)

📊 **Portfolio Project: End-to-End Supply Chain & Inventory Performance Dashboard**

I've developed a realistic **synthetic New Zealand distribution analytics case study** using 24 months of operational records and **153,503 order lines**.

The project brings together:
✅ Advanced Excel KPI scorecards and Power Query cleaning exercises
✅ SQL Server relational modelling, joins, CTEs, window functions and operational KPI queries
✅ Power BI star-schema design, reusable DAX measures and a six-page report build blueprint
✅ SAP-style purchase orders, material masters, goods receipts and inventory movement codes
✅ Operational insights covering **OTIF, inventory turnover, stockouts, backorders, supplier lead time, warehouse productivity and transport costs**

For example, the fictional operation records **65.75% OTIF** and **83.31% unit fill rate**. The analysis investigates why service problems can coexist with excess inventory, and outlines improvement opportunities across procurement, stock planning and delivery.

The repository includes validated datasets, Excel analysis, SQL scripts, DAX measures, report layout previews and a detailed management-insights report. The dashboard images are **data-derived design previews**; a live `.pbix` build is documented separately.

🔗 Project: https://github.com/YOUR-USERNAME/supply-chain-inventory-performance-dashboard

#SupplyChainAnalytics #InventoryManagement #Logistics #PowerBI #SQLServer #AdvancedExcel #DataAnalytics #NewZealandJobs

## CV project section

**Supply Chain & Inventory Analytics Portfolio Project** | Python, SQL Server, Excel, Power Query, Power BI/DAX design | 2026

- Created a reproducible 24-month synthetic distribution dataset with 153,503 order lines, five warehouse locations and linked purchasing, shipment and stock transaction records.
- Developed SQL Server relational schema, operational analytics scripts and a star-schema reporting layer; validated order fulfilment, inventory and freight KPIs.
- Built a formula-based Excel KPI workbook and designed a six-page Power BI reporting solution with documented DAX measures, exception analysis and management recommendations.

## 60-second recruiter explanation

"I created a portfolio project that simulates two years of supply chain operations for a New Zealand distribution company. It contains more than 153,000 order lines linked to products, suppliers, purchase orders, warehouse inventory and transport. I built a relational SQL Server design with analysis queries and a formula-driven Excel dashboard, and I documented a Power BI star schema and DAX measures for six reporting pages. My focus wasn't just charts. I validated OTIF, inventory turnover, unit fill rate and carrier performance, then identified high-backorder products, slow suppliers and warehouse productivity gaps. Because the data is synthetic, I can share the full project openly on GitHub. It demonstrates how I approach business problems through data modelling, KPI definitions and practical operational improvement."

## Interview questions and answer pointers

1. **Why synthetic data?** Share reproducible, privacy-safe operations with controlled defects and known truth.
2. **What is the grain of FactOrders?** One order line; COUNTROWS is not an order count.
3. **Why not sum monthly inventory?** Stock is semi-additive across date; use latest snapshot or average balances for turnover.
4. **How do you define OTIF?** Delivered orders with delivery date on/before required date and no unfulfilled units, divided by eligible delivered orders.
5. **Why do OTIF and fill rate differ?** OTIF is delivered-order event-based; fill rate is units shipped divided by units ordered.
6. **How can stockouts happen with high inventory?** Inventory misallocation by SKU/warehouse and unbalanced replenishment.
7. **What does movement type 101 mean?** Simulated PO goods receipt; 601 sales issue; 561 opening stock posting.
8. **How do you prevent double counting freight?** Calculate from shipment grain, not after joining multiple order lines.
9. **How would you evaluate slow-moving stock?** Current proxy measures time since last movement; for proper FIFO ageing I would collect lot receipt dates.
10. **What would you change next?** Add accurate actual lot ageing, historical demand forecasting, ABC/XYZ segmentation and a fully built/reconciled Power BI Desktop `.pbix`.
11. **How do you compare suppliers fairly?** Separate late receipt rate from open POs; compare promised vs actual lead time by line and product family.
12. **How do you validate KPI consistency?** Reconcile SQL and DAX against Python-validated global totals and test slicer contexts.
13. **Why is WH03 less productive?** Observed lower units/hour; possible drivers need normalised pick-type and route analyses, not speculation.
14. **Is this from a real SAP company?** No. It is an explicitly synthetic case with SAP-like field conventions and movement types.
15. **Where can I see the live Power BI report?** A six-page report blueprint and visual previews are provided; native Power BI report work is a separate desktop build step.
'''
(LINK/'profile_kit.md').write_text(linkedin,encoding='utf-8')
print('Documentation generated:',len(counts),'source data files')
