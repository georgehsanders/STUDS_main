import os
import re
import csv
import io
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)

INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input')
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed')

# --- Status constants ---
STATUS_UPDATED = "Updated"
STATUS_DISCREPANCY = "Discrepancy Detected"
STATUS_INCOMPLETE = "Incomplete — Missing File"

# --- Store name mapping placeholder ---
# v2: Replace this with a mapping of store ID -> store name.
# Example: STORE_NAMES = {"1001": "Downtown", "1002": "Westside"}
STORE_NAMES = {}

# --- File pattern regexes ---
RE_SKU_LIST = re.compile(r'^SKU_List_(\d{2}_\d{2}_\d{2})\.csv$')
RE_VARIANCE = re.compile(r'^(\d+)_Variance\.csv$')
RE_AUDIT_TRAIL = re.compile(r'^AuditTrail_(\d{2}_\d{2}_\d{2})\.csv$')

# --- SKU exclusion ---
RE_RS_PREFIX = re.compile(r'^RS', re.IGNORECASE)


def is_excluded_sku(sku):
    """Return True if this SKU should be excluded (starts with RS)."""
    return bool(RE_RS_PREFIX.match(sku))


def clean_csv_content(raw_bytes):
    """Strip BOM, normalize line endings, decode to string."""
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        raw_bytes = raw_bytes[3:]
    text = raw_bytes.decode('utf-8', errors='replace')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text


def parse_csv(filepath):
    """Read a CSV file, stripping BOM and whitespace from headers and values."""
    with open(filepath, 'rb') as f:
        raw = f.read()
    text = clean_csv_content(raw)
    reader = csv.DictReader(io.StringIO(text))
    reader.fieldnames = [h.strip() for h in reader.fieldnames]
    rows = []
    for row in reader:
        cleaned = {k.strip(): v.strip() for k, v in row.items()}
        rows.append(cleaned)
    return rows


def scan_input_files():
    """Scan /input/ and classify files by regex. Returns dict of classified files and warnings."""
    sku_lists = []
    variance_files = {}
    audit_trails = []
    warnings = []
    unrecognized = []

    if not os.path.isdir(INPUT_DIR):
        warnings.append("Input directory does not exist.")
        return {
            'sku_lists': sku_lists,
            'variance_files': variance_files,
            'audit_trails': audit_trails,
            'warnings': warnings,
            'unrecognized': unrecognized,
        }

    for filename in os.listdir(INPUT_DIR):
        filepath = os.path.join(INPUT_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        m_sku = RE_SKU_LIST.match(filename)
        m_var = RE_VARIANCE.match(filename)
        m_audit = RE_AUDIT_TRAIL.match(filename)

        if m_sku:
            sku_lists.append((filename, m_sku.group(1)))
        elif m_var:
            store_id = m_var.group(1)
            variance_files[store_id] = filename
        elif m_audit:
            audit_trails.append((filename, m_audit.group(1)))
        else:
            unrecognized.append(filename)
            print(f"[WARN] Unrecognized file in /input/: {filename}")

    # If multiple SKU lists, pick most recent by date string
    if len(sku_lists) > 1:
        sku_lists.sort(key=lambda x: x[1], reverse=True)
        warnings.append(f"Multiple SKU lists found. Using most recent: {sku_lists[0][0]}")
    if len(audit_trails) > 1:
        audit_trails.sort(key=lambda x: x[1], reverse=True)
        warnings.append(f"Multiple audit trails found. Using most recent: {audit_trails[0][0]}")

    if not sku_lists:
        warnings.append("No weekly SKU list file found. Stores cannot be reconciled.")
    if not audit_trails:
        warnings.append("No audit trail file found. Stores cannot be reconciled.")

    return {
        'sku_lists': sku_lists,
        'variance_files': variance_files,
        'audit_trails': audit_trails,
        'warnings': warnings,
        'unrecognized': unrecognized,
    }


def load_sku_list(filepath):
    """Load the weekly SKU list. Returns a set of SKU strings (excluding RS SKUs)."""
    rows = parse_csv(filepath)
    skus = set()
    for row in rows:
        sku = row.get('SKU', '').strip()
        if sku and not is_excluded_sku(sku):
            skus.add(sku)
    return skus


def load_variance(filepath):
    """Load a per-store variance file. Returns list of dicts with parsed numeric fields."""
    rows = parse_csv(filepath)
    result = []
    for row in rows:
        sku = row.get('Sku', row.get('SKU', '')).strip()
        if not sku or is_excluded_sku(sku):
            continue
        try:
            counted = int(float(row.get('Counted Units', '0').strip() or '0'))
        except (ValueError, TypeError):
            counted = 0
        try:
            onhand = int(float(row.get('Onhand Units', '0').strip() or '0'))
        except (ValueError, TypeError):
            onhand = 0
        try:
            unit_variance = int(float(row.get('Unit Variance', '0').strip() or '0'))
        except (ValueError, TypeError):
            unit_variance = counted - onhand
        result.append({
            'sku': sku,
            'description': row.get('Description', ''),
            'counted_units': counted,
            'onhand_units': onhand,
            'unit_variance': unit_variance,
            'areas': row.get('Areas', ''),
        })
    return result


def load_audit_trail(filepath):
    """Load global audit trail. Returns list of dicts with parsed fields."""
    rows = parse_csv(filepath)
    result = []
    for row in rows:
        sku = row.get('SKU', '').strip()
        if not sku or is_excluded_sku(sku):
            continue
        ref = row.get('Reference', '').strip()
        try:
            qty = int(float(row.get('Quantity', '0').strip() or '0'))
        except (ValueError, TypeError):
            qty = 0
        result.append({
            'product_id': row.get('Product ID', '').strip(),
            'sku': sku,
            'product_name': row.get('Product Name', '').strip(),
            'options': row.get('Options', '').strip(),
            'quantity': qty,
            'price': row.get('Price', '').strip(),
            'reference': ref,
            'warehouse': row.get('Warehouse', '').strip(),
            'date': row.get('Date', '').strip(),
            'movement_id': row.get('Movement ID', '').strip(),
        })
    return result


def get_audit_date_range(audit_rows):
    """Return (min_date_str, max_date_str) from audit trail rows."""
    dates = [r['date'] for r in audit_rows if r['date']]
    if not dates:
        return (None, None)
    return (min(dates), max(dates))


def reconcile_store(store_id, weekly_skus, variance_data, audit_rows):
    """
    Reconcile a single store. Completely decoupled from Flask.

    Args:
        store_id: string store identifier
        weekly_skus: set of SKU strings from the weekly SKU list (already RS-filtered)
        variance_data: list of dicts from load_variance (already RS-filtered)
        audit_rows: list of dicts from load_audit_trail (global, already RS-filtered)

    Returns:
        dict with keys: store_id, status, active_skus, discrepancy_count,
                        net_discrepancy, sku_details
    """
    # Step 1 — active SKUs = intersection of weekly list and variance file SKUs, minus RS
    variance_skus = {item['sku'] for item in variance_data}
    active_skus = {s for s in (weekly_skus & variance_skus) if not is_excluded_sku(s)}

    # Build lookup for variance data
    variance_lookup = {item['sku']: item for item in variance_data}

    # Filter audit trail to this store, relevant references
    store_audit = [
        r for r in audit_rows
        if r['warehouse'] == store_id
        and ('stock update' in r['reference'].lower() or 'stock check' in r['reference'].lower())
    ]

    # Build audit lookup: SKU -> sum of quantity
    audit_by_sku = {}
    for r in store_audit:
        audit_by_sku[r['sku']] = audit_by_sku.get(r['sku'], 0) + r['quantity']

    sku_details = []
    discrepancy_count = 0
    net_discrepancy = 0

    for sku in sorted(active_skus):
        var_item = variance_lookup[sku]
        required_push = var_item['unit_variance']  # Step 2
        actual_push = audit_by_sku.get(sku, 0)     # Step 3
        discrepancy = required_push - actual_push   # Step 4

        detail = {
            'sku': sku,
            'description': var_item['description'],
            'counted_units': var_item['counted_units'],
            'onhand_units': var_item['onhand_units'],
            'unit_variance': required_push,
            'actual_push': actual_push,
            'discrepancy': discrepancy,
        }
        sku_details.append(detail)

        if discrepancy != 0:
            discrepancy_count += 1
            net_discrepancy += discrepancy

    # Step 5 — status
    if discrepancy_count > 0:
        status = STATUS_DISCREPANCY
    else:
        status = STATUS_UPDATED

    return {
        'store_id': store_id,
        'status': status,
        'active_sku_count': len(active_skus),
        'discrepancy_count': discrepancy_count,
        'net_discrepancy': net_discrepancy,
        'sku_details': [d for d in sku_details if d['discrepancy'] != 0],
    }


def run_reconciliation():
    """
    Full reconciliation pipeline. Scans /input/, loads files, reconciles all stores.
    Returns a results dict suitable for rendering.
    """
    scan = scan_input_files()
    warnings = list(scan['warnings'])
    stores = []
    sku_list_filename = None
    sku_count = 0
    audit_date_min = None
    audit_date_max = None

    # Load SKU list
    weekly_skus = set()
    if scan['sku_lists']:
        sku_list_filename = scan['sku_lists'][0][0]
        try:
            weekly_skus = load_sku_list(os.path.join(INPUT_DIR, sku_list_filename))
            sku_count = len(weekly_skus)
        except Exception as e:
            print(f"[ERROR] Failed to parse SKU list {sku_list_filename}: {e}")
            warnings.append(f"Failed to parse SKU list: {e}")

    # Load audit trail
    audit_rows = []
    audit_filename = None
    if scan['audit_trails']:
        audit_filename = scan['audit_trails'][0][0]
        try:
            audit_rows = load_audit_trail(os.path.join(INPUT_DIR, audit_filename))
            audit_date_min, audit_date_max = get_audit_date_range(audit_rows)
        except Exception as e:
            print(f"[ERROR] Failed to parse audit trail {audit_filename}: {e}")
            warnings.append(f"Failed to parse audit trail: {e}")

    can_reconcile = bool(weekly_skus) and (scan['audit_trails'] is not None and len(scan['audit_trails']) > 0)

    # Collect all store IDs from variance files AND audit trail warehouses
    all_store_ids = set(scan['variance_files'].keys())
    for row in audit_rows:
        wh = row['warehouse']
        if wh:
            all_store_ids.add(wh)

    for store_id in sorted(all_store_ids, key=lambda x: int(x) if x.isdigit() else x):
        # Store has no variance file → Incomplete
        if store_id not in scan['variance_files']:
            stores.append({
                'store_id': store_id,
                'status': STATUS_INCOMPLETE,
                'active_sku_count': 0,
                'discrepancy_count': 0,
                'net_discrepancy': 0,
                'sku_details': [],
            })
            continue
        if not can_reconcile:
            stores.append({
                'store_id': store_id,
                'status': STATUS_INCOMPLETE,
                'active_sku_count': 0,
                'discrepancy_count': 0,
                'net_discrepancy': 0,
                'sku_details': [],
            })
            continue

        variance_filename = scan['variance_files'][store_id]
        try:
            variance_data = load_variance(os.path.join(INPUT_DIR, variance_filename))
        except Exception as e:
            print(f"[ERROR] Failed to parse variance file {variance_filename}: {e}")
            warnings.append(f"Failed to parse {variance_filename}: {e}")
            stores.append({
                'store_id': store_id,
                'status': STATUS_INCOMPLETE,
                'active_sku_count': 0,
                'discrepancy_count': 0,
                'net_discrepancy': 0,
                'sku_details': [],
            })
            continue

        result = reconcile_store(store_id, weekly_skus, variance_data, audit_rows)
        stores.append(result)

    # Summary counts
    count_updated = sum(1 for s in stores if s['status'] == STATUS_UPDATED)
    count_discrepancy = sum(1 for s in stores if s['status'] == STATUS_DISCREPANCY)
    count_incomplete = sum(1 for s in stores if s['status'] == STATUS_INCOMPLETE)

    return {
        'stores': stores,
        'warnings': warnings,
        'sku_list_filename': sku_list_filename,
        'sku_count': sku_count,
        'audit_date_min': audit_date_min,
        'audit_date_max': audit_date_max,
        'total_stores': len(stores),
        'count_updated': count_updated,
        'count_discrepancy': count_discrepancy,
        'count_incomplete': count_incomplete,
        'last_loaded': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


# --- Flask routes ---

@app.route('/')
def index():
    results = run_reconciliation()
    return render_template('index.html', data=results)


@app.route('/refresh', methods=['POST'])
def refresh():
    results = run_reconciliation()
    return jsonify(results)


if __name__ == '__main__':
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print(f"[STUDS] Input directory: {INPUT_DIR}")
    print(f"[STUDS] Starting on http://localhost:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
