# Management insights & improvement plan (synthetic results)

**All conclusions below are exploratory interpretations of deliberately fictional operating records. No real employer, customer or external supplier performance is represented.** Metrics were computed from the full processed CSVs, not estimated from plots. Proposed impact is a test hypothesis, not a realised saving.

## Page 1 — Executive Overview

1. Sales total **NZD 198,621,923.48**, gross profit **NZD 53,843,788.85**, gross margin **27.11%** over 24 months. Recommendation: protect high-margin fast movers before low-turn surplus replenishment.
2. OTIF is **65.75%**, meaning more than one-third of eligible delivered orders miss the combined service requirement. Recommendation: review customer promises and item availability by date, not on-time-only metrics.
3. **380,813 units** remain backordered from an ordered demand base of 2,281,553, resulting in **83.31% unit fill rate**. Recommendation: create SKU/warehouse shortage alerts and assign replenishment owners.
4. Freight consumes **NZD 9,323,808.00**, around **4.69% of dispatched sales**. Recommendation: carrier-cost/service segmentation by lane before negotiating tariffs.
5. Latest closing stock is **NZD 108,194,990.59**, with a low **0.98× annualised turnover**. Recommendation: monitor both cash tied up and service level together; avoid indiscriminate stock cuts.

## Page 2 — Inventory Performance

1. Final month closing inventory is **NZD 108,194,990.59** compared with two-year mean month-end **NZD 73,873,941.28**. Recommendation: make a stock-build bridge by receipts vs shipment issues.
2. `P0001` (Beverages) creates **27,713 backordered units**, the largest individual SKU. Recommendation: examine demand distribution and reorder settings specifically at affected warehouses.
3. `P0269` ties up **NZD 2,030,730.00** at closing inventory. Recommendation: evaluate its stock cover, discontinue automatic ordering where holdings materially exceed the safety requirement.
4. Over the 24 month-ends, **8.5%** of product × warehouse observation points have zero available stock; in the final month it rises to **10.33%**. Recommendation: service-focused ABC/XYZ stocking policy with different reorder rules.
5. **NZD 288,432.97** meets the strict 90+ days-since-last-movement proxy at final snapshot. A receipt resets this timer; this **understates possible FIFO-aged on-hand stock**. Recommendation: gather lot receipt dates for genuine inventory-age analysis.

## Page 3 — Supplier Performance

1. Mean completed PO-line lead time is **20.26 days**. Recommendation: segment vendor promises and actual performance using line-level receipt dates.
2. `SUP052` averages **48.73 days** among 500 received lines, with **0.0% recorded on-time**. Recommendation: test contract feasibility and order-release timing; do not assume the data identifies causation.
3. `SUP039` has the highest simulated total PO-line purchase value at around **NZD 4,998,291.96**. Recommendation: focus supplier review on both spend concentration and service reliability.
4. Several suppliers have 0% on-time receipts in the simulation despite completed receipts. Recommendation: check promise-date quality and agreed buffers before supplier sanctions.
5. Open PO lines are excluded from completed lead-time averages. Recommendation: add a separate overdue-open PO report so the lead-time metric does not hide non-receipt risk.

## Page 4 — Warehouse Performance

1. `WH03` averages **22.01 units per labour hour**, the lowest observed site, compared with `WH01` at **44.55**. Recommendation: measure travel paths, pick density and wave-planning process, adjusting for product mix.
2. All warehouses together processed **1,900,740 units** using **62,699.37 labour hours**. Recommendation: use weighted output/hours, not the mean of daily ratios.
3. Global exact-match physical stock count accuracy is **90.53%**. Recommendation: cycle counts prioritised by high-value discrepancies and repeated variance SKUs.
4. `WH04` has the weakest site stock-record accuracy in the simulation at **89.81%**. Recommendation: audit movement discipline, recording timing, bin transfers and picking exceptions.
5. Labour hours include inactive periods, so units/hour measures overall shift efficiency rather than individual worker performance. Recommendation: add labour job codes before attributing the gap to staff.

## Page 5 — Transportation Performance

1. `CR04` averages **NZD 302.96 per shipment** with **96.83% on-time delivered service**. Recommendation: reserve this premium service for urgent/high-value lanes, subject to volume and route mix controls.
2. `CR03` averages **NZD 118.46 per shipment**, but its on-time result is only **83.01%**. Recommendation: analyse service improvement potential and customer penalty costs before selecting solely on price.
3. In total, freight expense is **NZD 9,323,808.00**, roughly **NZD 388,492 per month**. Recommendation: monitor lane- and carrier-normalised cost per shipment.
4. Cost-per-order uses shipped orders (there is one shipment/order here); a future split-delivery system will require distinct order counts. Recommendation: preserve shipment and order keys separately in the data model.
5. Carrier comparison is descriptive, not causal; distances, volumes and urgency vary. Recommendation: run like-for-like lane analyses before signing new contracts.

## Page 6 — Customer and Order Performance

1. `Canterbury` has the lowest measured regional delivered-order OTIF at **64.82%**. Recommendation: focus root-cause exception codes, rather than blanket delivery promises.
2. `Wellington` has the highest cumulative backorders: **79,487 units**. Recommendation: isolate category/SKU concentration before allocating stock transfers.
3. `Wellington` also produces the greatest sales of the five destination regions: **NZD 41,741,951.10**. Recommendation: evaluate fill-rate improvement in proportion to region demand and customer priority.
4. The combined unit fill rate of **83.31%** is not interchangeable with **65.75% OTIF**; one is item-unit based and one is delivered-order event based. Recommendation: report both service perspectives.
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
