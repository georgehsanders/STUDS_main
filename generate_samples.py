"""Generate realistic sample input files for 40 stores."""
import csv
import os
import random

random.seed(42)

INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input')

SKUS = [
    ("EAR-TI-GLD", "Tiny Gold Studs"),
    ("EAR-TI-SLV", "Tiny Silver Studs"),
    ("EAR-HG-GLD", "Huggie Gold Hoops"),
    ("EAR-HG-SLV", "Huggie Silver Hoops"),
    ("EAR-FL-GLD", "Flat Back Gold Labret"),
    ("EAR-FL-SLV", "Flat Back Silver Labret"),
    ("EAR-CZ-CLR", "CZ Clear Round Stud"),
    ("EAR-CZ-BLK", "CZ Black Round Stud"),
    ("EAR-OP-WHT", "Opal White Cabochon"),
    ("EAR-OP-PNK", "Opal Pink Cabochon"),
    ("EAR-ST-MN", "Star Moon Charm"),
    ("EAR-ST-HRT", "Star Heart Charm"),
    ("EAR-BZ-GLD", "Bezel Set Gold"),
    ("EAR-BZ-SLV", "Bezel Set Silver"),
    ("EAR-CL-DBL", "Cluster Double Stack"),
    ("EAR-CL-TRP", "Cluster Triple Stack"),
    ("EAR-CH-LNK", "Chain Link Drop"),
    ("EAR-CH-THR", "Chain Threader"),
    ("EAR-DG-RND", "Dangle Round Drop"),
    ("EAR-DG-OVL", "Dangle Oval Drop"),
    ("EAR-CB-SQ", "Cabochon Square"),
    ("EAR-CB-TRI", "Cabochon Triangle"),
    ("EAR-PL-THN", "Plain Thin Ring"),
    ("EAR-PL-THK", "Plain Thick Ring"),
]

RS_SKUS = [
    ("RS-REPAIR-01", "Repair Kit Standard"),
    ("RS-REPAIR-02", "Repair Kit Premium"),
]

AREAS = ["Display Case A", "Display Case B", "Display Case C", "Display Case D",
         "Display Case E", "Piercing Station 1", "Piercing Station 2", "Wall Rack", "Back Stock"]

PRICES = {
    "EAR-TI-GLD": 24.99, "EAR-TI-SLV": 22.99, "EAR-HG-GLD": 34.99,
    "EAR-HG-SLV": 32.99, "EAR-FL-GLD": 29.99, "EAR-FL-SLV": 27.99,
    "EAR-CZ-CLR": 19.99, "EAR-CZ-BLK": 19.99, "EAR-OP-WHT": 25.99,
    "EAR-OP-PNK": 27.99, "EAR-ST-MN": 18.99, "EAR-ST-HRT": 18.99,
    "EAR-BZ-GLD": 36.99, "EAR-BZ-SLV": 34.99, "EAR-CL-DBL": 42.99,
    "EAR-CL-TRP": 48.99, "EAR-CH-LNK": 22.99, "EAR-CH-THR": 22.99,
    "EAR-DG-RND": 26.99, "EAR-DG-OVL": 28.99, "EAR-CB-SQ": 31.99,
    "EAR-CB-TRI": 31.99, "EAR-PL-THN": 14.99, "EAR-PL-THK": 16.99,
}

DATES = [
    "03/02/2026 08:{:02d}", "03/02/2026 14:{:02d}",
    "03/03/2026 09:{:02d}", "03/03/2026 15:{:02d}",
    "03/04/2026 10:{:02d}", "03/04/2026 16:{:02d}",
    "03/05/2026 09:{:02d}", "03/05/2026 14:{:02d}",
    "03/06/2026 10:{:02d}", "03/06/2026 15:{:02d}",
    "03/07/2026 08:{:02d}", "03/07/2026 11:{:02d}",
]

# --- Store assignments ---
# Incomplete stores (no variance file): 7 stores
INCOMPLETE_STORES = {6, 13, 19, 25, 31, 37, 40}
# Updated stores (all pushes match): ~15 stores
UPDATED_STORES = {2, 4, 7, 9, 11, 15, 17, 20, 22, 24, 27, 30, 33, 36, 39}
# Discrepancy stores: the remaining ~18 stores
ALL_STORES = set(range(1, 41))
DISCREPANCY_STORES = ALL_STORES - INCOMPLETE_STORES - UPDATED_STORES

print(f"Updated: {len(UPDATED_STORES)} | Discrepancy: {len(DISCREPANCY_STORES)} | Incomplete: {len(INCOMPLETE_STORES)}")

# --- Generate SKU list ---
with open(os.path.join(INPUT_DIR, "SKU_List_03_07_26.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["SKU ", "Product Name"])  # trailing space per spec
    for sku, name in SKUS:
        w.writerow([sku, name])
    for sku, name in RS_SKUS:
        w.writerow([sku, name])
print(f"SKU list: {len(SKUS)} active + {len(RS_SKUS)} RS-excluded")

# --- Per-store data generation ---
mv_counter = 90000
audit_rows = []

def make_date():
    tpl = random.choice(DATES)
    return tpl.format(random.randint(0, 59))

def add_audit(sku, name, qty, ref, warehouse, price=None):
    global mv_counter
    mv_counter += 1
    audit_rows.append({
        "Product ID": str(4000 + list(s[0] for s in SKUS).index(sku)),
        "SKU": sku,
        "Product Name": name,
        "Options": "",
        "Quantity": str(qty),
        "Price": str(price or PRICES.get(sku, 19.99)),
        "Reference": ref,
        "Warehouse": str(warehouse),
        "Date": make_date(),
        "Movement ID": f"MV-{mv_counter}",
    })

for store_id in sorted(ALL_STORES - INCOMPLETE_STORES):
    # Generate variance data for this store
    rows = []
    # Each store counts most or all SKUs
    store_skus = list(SKUS)
    # Some stores only count a subset
    if store_id in {1, 8, 14, 28, 34}:
        store_skus = random.sample(SKUS, random.randint(14, 20))

    for sku, name in store_skus:
        onhand = random.randint(2, 35)
        area = random.choice(AREAS)

        if store_id in UPDATED_STORES:
            # These stores have variances but all get pushed correctly
            if random.random() < 0.6:
                variance = 0
                counted = onhand
            else:
                variance = random.choice([-3, -2, -1, 1, 2, 3])
                counted = onhand + variance
        else:
            # Discrepancy stores: some variances won't be pushed
            if random.random() < 0.4:
                variance = 0
                counted = onhand
            else:
                variance = random.choice([-5, -4, -3, -2, -1, 1, 2])
                counted = onhand + variance

        if counted < 0:
            counted = 0
            variance = counted - onhand

        rows.append({
            "Sku": sku,
            "Description": name,
            "Counted Units": str(counted),
            "Onhand Units": str(onhand),
            "Unit Variance": str(variance),
            "Areas": area,
        })

    # Add an RS SKU to some stores
    if random.random() < 0.3:
        rs_sku, rs_name = random.choice(RS_SKUS)
        rows.append({
            "Sku": rs_sku,
            "Description": rs_name,
            "Counted Units": "5",
            "Onhand Units": "5",
            "Unit Variance": "0",
            "Areas": "Back Stock",
        })

    # Write variance file
    with open(os.path.join(INPUT_DIR, f"{store_id}_Variance.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Sku", "Description", "Counted Units", "Onhand Units", "Unit Variance", "Areas"])
        w.writeheader()
        w.writerows(rows)

    # Generate audit trail entries for this store
    for r in rows:
        sku = r["Sku"]
        if sku.upper().startswith("RS"):
            continue
        variance = int(r["Unit Variance"])
        name = r["Description"]

        if variance == 0:
            # No push needed. Maybe add some noise (sales orders, goods in)
            if random.random() < 0.2:
                add_audit(sku, name, random.choice([-2, -1, 1, 3]),
                          random.choice(["Sales Order SO-" + str(random.randint(4000,4999)),
                                        "Goods In PO-" + str(random.randint(2000,2999))]),
                          store_id)
            continue

        if store_id in UPDATED_STORES:
            # Push the exact variance
            ref = random.choice(["Stock Update", "Stock Check"])
            add_audit(sku, name, variance, ref, store_id)
        else:
            # Discrepancy: some get pushed, some don't, some get partial
            roll = random.random()
            if roll < 0.35:
                # Correctly pushed
                ref = random.choice(["Stock Update", "Stock Check"])
                add_audit(sku, name, variance, ref, store_id)
            elif roll < 0.55:
                # Partial push
                partial = variance // 2 if abs(variance) > 1 else 0
                if partial != 0:
                    add_audit(sku, name, partial, "Stock Update", store_id)
                # else: no push at all → discrepancy
            # else: not pushed at all → discrepancy

        # Sprinkle in noise entries (sales, goods in) that should NOT count
        if random.random() < 0.15:
            add_audit(sku, name, random.choice([-3, -1, 2]),
                      "Sales Order SO-" + str(random.randint(4000, 4999)),
                      store_id)

# Add some cross-store noise in the audit trail
for _ in range(50):
    sku, name = random.choice(SKUS)
    store_id = random.randint(1, 40)
    ref = random.choice(["Sales Order SO-" + str(random.randint(4000,4999)),
                          "Goods In PO-" + str(random.randint(2000,2999)),
                          "Transfer T-" + str(random.randint(100,999))])
    add_audit(sku, name, random.choice([-4, -3, -2, -1, 1, 2, 3, 5]), ref, store_id)

# Shuffle audit rows for realism
random.shuffle(audit_rows)

# Write audit trail
with open(os.path.join(INPUT_DIR, "AuditTrail_03_07_26.csv"), "w", newline="") as f:
    fields = ["Product ID", "SKU", "Product Name", "Options", "Quantity", "Price",
              "Reference", "Warehouse", "Date", "Movement ID"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(audit_rows)

print(f"Audit trail: {len(audit_rows)} rows")
print(f"Variance files: {len(ALL_STORES - INCOMPLETE_STORES)}")
print("Done.")
