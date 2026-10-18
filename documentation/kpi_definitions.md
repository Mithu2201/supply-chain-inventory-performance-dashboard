# KPI definitions and safe aggregation logic

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

- **date_start:** 2024-10-01
- **date_end:** 2026-09-30
- **orders:** 63,500
- **order_lines:** 153,503
- **purchase_orders:** 15,500
- **po_lines:** 31,911
- **products:** 480
- **net_sales_nzd:** 198,621,923.48
- **cogs_nzd:** 144,778,134.63
- **gross_profit_nzd:** 53,843,788.85
- **gross_margin_pct:** 27.11
- **eligible_delivered_orders:** 60,236
- **otif_pct:** 65.75
- **on_time_pct:** 88.69
- **in_full_pct:** 74.11
- **backorder_units:** 380,813
- **ordered_units:** 2,281,553
- **shipped_units:** 1,900,740
- **fill_rate_pct:** 83.31
- **latest_inventory_nzd:** 108,194,990.59
- **avg_month_end_inventory_nzd:** 73,873,941.28
- **turnover_2y:** 1.96
- **annualised_turnover:** 0.98
- **inventory_accuracy_pct:** 90.53
- **stockout_snapshot_pct:** 8.5
- **mean_supplier_receipt_lead_days:** 20.26
- **freight_total_nzd:** 9,323,808.0
- **picked_units:** 1,900,740
- **labour_hours:** 62,699.37

**Reconciliation warning:** `Stockout Rate %` on the current-period Power BI card uses **latest selected snapshot**, while `validated_metrics.json` includes **all 24 monthly snapshot observations** (`stockout_snapshot_pct`). These naturally differ. Likewise, `OTIF %` is shipment **delivery-date** filtered in Power BI but uses a full two-year delivered **order cohort** in the global Python audit: late-September orders delivered after September are not eligible for the Python global baseline.
