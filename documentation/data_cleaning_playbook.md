# Data cleaning lab — audit, repair and review

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
