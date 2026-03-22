# STUDS Stock Check Dashboard

Detects stores that failed to push Omnicount variance data into Brightpearl by comparing per-store variance exports against the global Brightpearl audit trail.

## How to Run

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` in your browser.

## Folder Structure

```
/app.py              — Flask app + reconciliation logic
/templates/index.html — Dashboard frontend
/static/style.css    — Styles
/input/              — Drop all weekly files here
/processed/          — (reserved for future use)
/requirements.txt    — Python dependencies
/Procfile            — For Railway smoke-test deployment only
```

## Input File Naming Conventions

Drop all files into `/input/`. The app identifies each file by its filename pattern:

| File Type | Pattern | Example | Scope |
|---|---|---|---|
| Weekly SKU List | `SKUList_MM_DD_YY.csv` | `SKUList_03_07_26.csv` | One file, all stores |
| Per-Store Variance | `{storeID}_Variance.csv` or `{storeID}_Variance_MM-DD-YY.csv` | `002_Variance_03-09-26.csv` | One file per store |
| Global Audit Trail | `AuditTrail_MM_DD_YY.csv` or `AuditTrail_MM-DD-YY.csv` | `AuditTrail_03_07_26.csv` | One file, all stores |

- If multiple SKU lists or audit trails are found, the most recently dated one is used (with a warning).
- Unrecognized files are logged to the terminal and skipped.

## SKU Exclusion

Any SKU beginning with `RS` (case-insensitive) is excluded from all reconciliation and display.

## Reconciliation Logic

For each store with a variance file:
1. **Assigned SKUs** = (weekly SKU list) ∩ (store variance SKUs) − (RS-prefix SKUs)
2. **Required push** = Unit Variance from the variance file
3. **Actual push** = Sum of Quantity from audit trail rows matching the store + SKU where Reference contains "Stock Update" or "Stock Check"
4. **Discrepancy** = required push − actual push
5. **Status**: `Updated` if all discrepancies are zero, `Discrepancy Detected` if any are non-zero, `Incomplete — Missing File` if files are missing, `Incomplete — Unrecognized File Format` if variance file has unexpected columns

## Variance File Schema Validation

Expected columns: Sku, Description, Counted Units, Onhand Units, Unit Variance. Legacy format (productid, sku, quantity, location, item cost price) is also accepted. Files matching neither schema are flagged as unrecognized.

## Notes

- **Store names**: The Warehouse field in the audit trail (e.g., "002 NY Hudson Yards") is used to match stores by numeric prefix to variance file store IDs.
- The `Procfile` is included for Railway smoke-test deployment only. This is a local tool, not a hosted service.
