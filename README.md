# STUDS Inventory Continuity Dashboard

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
| Weekly SKU List | `SKU_List_MM_DD_YY.csv` | `SKU_List_03_07_26.csv` | One file, all stores |
| Per-Store Variance | `{storeID}_Variance.csv` | `1001_Variance.csv` | One file per store |
| Global Audit Trail | `AuditTrail_MM_DD_YY.csv` | `AuditTrail_03_07_26.csv` | One file, all stores |

- If multiple SKU lists or audit trails are found, the most recently dated one is used (with a warning).
- Unrecognized files are logged to the terminal and skipped.

## SKU Exclusion

Any SKU beginning with `RS` (case-insensitive) is excluded from all reconciliation and display.

## Reconciliation Logic

For each store with a variance file:
1. **Active SKUs** = (weekly SKU list) ∩ (store variance SKUs) − (RS-prefix SKUs)
2. **Required push** = Unit Variance from the variance file
3. **Actual push** = Sum of Quantity from audit trail rows matching the store + SKU where Reference contains "Stock Update" or "Stock Check"
4. **Discrepancy** = required push − actual push
5. **Status**: `Updated` if all discrepancies are zero, `Discrepancy Detected` if any are non-zero, `Incomplete — Missing File` if files are missing

## Notes

- **Store names**: v2 will add a store ID → name mapping. For now, only store IDs are displayed. See the `STORE_NAMES` placeholder in `app.py`.
- The `Procfile` is included for Railway smoke-test deployment only. This is a local tool, not a hosted service.
