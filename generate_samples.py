"""Generate realistic sample input files for 40 stores with real column formats."""
import csv
import os
import random

random.seed(42)

INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input')

SKUS = [
    ("EAR-TI-GLD", "Tiny Gold Studs", 4000),
    ("EAR-TI-SLV", "Tiny Silver Studs", 4001),
    ("EAR-HG-GLD", "Huggie Gold Hoops", 4002),
    ("EAR-HG-SLV", "Huggie Silver Hoops", 4003),
    ("EAR-FL-GLD", "Flat Back Gold Labret", 4004),
    ("EAR-FL-SLV", "Flat Back Silver Labret", 4005),
    ("EAR-CZ-CLR", "CZ Clear Round Stud", 4006),
    ("EAR-CZ-BLK", "CZ Black Round Stud", 4007),
    ("EAR-OP-WHT", "Opal White Cabochon", 4008),
    ("EAR-OP-PNK", "Opal Pink Cabochon", 4009),
    ("EAR-ST-MN", "Star Moon Charm", 4010),
    ("EAR-ST-HRT", "Star Heart Charm", 4011),
    ("EAR-BZ-GLD", "Bezel Set Gold", 4012),
    ("EAR-BZ-SLV", "Bezel Set Silver", 4013),
    ("EAR-CL-DBL", "Cluster Double Stack", 4014),
    ("EAR-CL-TRP", "Cluster Triple Stack", 4015),
    ("EAR-CH-LNK", "Chain Link Drop", 4016),
    ("EAR-CH-THR", "Chain Threader", 4017),
    ("EAR-DG-RND", "Dangle Round Drop", 4018),
    ("EAR-DG-OVL", "Dangle Oval Drop", 4019),
    ("EAR-CB-SQ", "Cabochon Square", 4020),
    ("EAR-CB-TRI", "Cabochon Triangle", 4021),
    ("EAR-PL-THN", "Plain Thin Ring", 4022),
    ("EAR-PL-THK", "Plain Thick Ring", 4023),
]

RS_SKUS = [
    ("RS-REPAIR-01", "Repair Kit Standard", 5000),
    ("RS-REPAIR-02", "Repair Kit Premium", 5001),
]

LOCATIONS = ["Display Case A", "Display Case B", "Display Case C", "Display Case D",
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

# Store name map: store_id -> "NNN Location Name" format for Warehouse column
STORE_WAREHOUSE_NAMES = {
    1: "001 NY SoHo",
    2: "002 NY Williamsburg",
    3: "003 NY Upper East Side",
    4: "004 NY Hudson Yards",
    5: "005 NY Flatiron",
    6: "006 NJ Garden State Plaza",
    7: "007 NJ Short Hills",
    8: "008 CT Westfield",
    9: "009 MA Newbury Street",
    10: "010 MA Burlington",
    11: "011 PA King of Prussia",
    12: "012 PA Rittenhouse",
    13: "013 DC Georgetown",
    14: "014 FL Aventura",
    15: "015 FL Dadeland",
    16: "016 FL Sawgrass",
    17: "017 FL International Plaza",
    18: "018 GA Lenox Square",
    19: "019 GA Avalon",
    20: "020 TX NorthPark",
    21: "021 TX Domain",
    22: "022 TX Galleria",
    23: "023 IL Michigan Ave",
    24: "024 IL Oakbrook",
    25: "025 MN Mall of America",
    26: "026 CO Cherry Creek",
    27: "027 CO Park Meadows",
    28: "028 AZ Scottsdale Fashion",
    29: "029 AZ Biltmore",
    30: "030 NV Fashion Show",
    31: "031 CA Beverly Center",
    32: "032 CA Century City",
    33: "033 CA Fashion Island",
    34: "034 CA Stanford",
    35: "035 CA UTC San Diego",
    36: "036 CA Santa Monica",
    37: "037 WA Bellevue Square",
    38: "038 WA University Village",
    39: "039 OR Pioneer Place",
    40: "040 HI Ala Moana",
}

# --- Store assignments ---
INCOMPLETE_STORES = {6, 13, 19, 25, 31, 37, 40}
UPDATED_STORES = {2, 4, 7, 9, 11, 15, 17, 20, 22, 24, 27, 30, 33, 36, 39}
ALL_STORES = set(range(1, 41))
DISCREPANCY_STORES = ALL_STORES - INCOMPLETE_STORES - UPDATED_STORES

print(f"Updated: {len(UPDATED_STORES)} | Discrepancy: {len(DISCREPANCY_STORES)} | Incomplete: {len(INCOMPLETE_STORES)}")

# --- Generate SKU list ---
with open(os.path.join(INPUT_DIR, "SKUList_03_07_26.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["SKU", "Product Name"])
    for sku, name, _ in SKUS:
        w.writerow([sku, name])
    for sku, name, _ in RS_SKUS:
        w.writerow([sku, name])
print(f"SKU list: {len(SKUS)} active + {len(RS_SKUS)} RS-excluded")

# --- Per-store data generation ---
mv_counter = 90000
audit_rows = []


def make_date():
    tpl = random.choice(DATES)
    return tpl.format(random.randint(0, 59))


def add_audit(sku, name, qty, ref, store_id, price=None):
    global mv_counter
    mv_counter += 1
    warehouse_name = STORE_WAREHOUSE_NAMES.get(store_id, f"{store_id:03d} Unknown")
    product_id = None
    for s, _, pid in SKUS + RS_SKUS:
        if s == sku:
            product_id = str(pid)
            break
    audit_rows.append({
        "Product ID": product_id or str(4000),
        "SKU": sku,
        "Product Name": name,
        "Options": "",
        "Quantity": str(qty),
        "Price": str(price or PRICES.get(sku, 19.99)),
        "Reference": ref,
        "Warehouse": warehouse_name,
        "Date": make_date(),
        "Movement ID": f"MV-{mv_counter}",
    })


for store_id in sorted(ALL_STORES - INCOMPLETE_STORES):
    # Generate variance data with real column format: productid, sku, quantity, location, item cost price
    rows = []
    store_skus = list(SKUS)
    if store_id in {1, 8, 14, 28, 34}:
        store_skus = random.sample(SKUS, random.randint(14, 20))

    for sku, name, pid in store_skus:
        location = random.choice(LOCATIONS)

        if store_id in UPDATED_STORES:
            if random.random() < 0.6:
                quantity = 0
            else:
                quantity = random.choice([-3, -2, -1, 1, 2, 3])
        else:
            if random.random() < 0.4:
                quantity = 0
            else:
                quantity = random.choice([-5, -4, -3, -2, -1, 1, 2])

        rows.append({
            "productid": str(pid),
            "sku": sku,
            "quantity": str(quantity),
            "location": location,
            "item cost price": f"{PRICES.get(sku, 19.99):.2f}",
        })

    # Add an RS SKU to some stores
    if random.random() < 0.3:
        rs_sku, rs_name, rs_pid = random.choice(RS_SKUS)
        rows.append({
            "productid": str(rs_pid),
            "sku": rs_sku,
            "quantity": "0",
            "location": "Back Stock",
            "item cost price": "9.99",
        })

    # Write variance file with real column format
    with open(os.path.join(INPUT_DIR, f"{store_id}_Variance.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["productid", "sku", "quantity", "location", "item cost price"])
        w.writeheader()
        w.writerows(rows)

    # Generate audit trail entries for this store
    for r in rows:
        sku = r["sku"]
        if sku.upper().startswith("RS"):
            continue
        quantity = int(r["quantity"])
        # Find name
        name = ""
        for s, n, _ in SKUS:
            if s == sku:
                name = n
                break

        if quantity == 0:
            if random.random() < 0.2:
                add_audit(sku, name, random.choice([-2, -1, 1, 3]),
                          random.choice(["Sales Order SO-" + str(random.randint(4000, 4999)),
                                         "Goods In PO-" + str(random.randint(2000, 2999))]),
                          store_id)
            continue

        if store_id in UPDATED_STORES:
            ref = random.choice(["Stock Update", "Stock Check"])
            add_audit(sku, name, quantity, ref, store_id)
        else:
            roll = random.random()
            if roll < 0.35:
                ref = random.choice(["Stock Update", "Stock Check"])
                add_audit(sku, name, quantity, ref, store_id)
            elif roll < 0.55:
                partial = quantity // 2 if abs(quantity) > 1 else 0
                if partial != 0:
                    add_audit(sku, name, partial, "Stock Update", store_id)
            # else: not pushed at all

        if random.random() < 0.15:
            add_audit(sku, name, random.choice([-3, -1, 2]),
                      "Sales Order SO-" + str(random.randint(4000, 4999)),
                      store_id)

# Ensure all incomplete stores have at least some audit trail entries
for store_id in sorted(INCOMPLETE_STORES):
    for _ in range(random.randint(3, 8)):
        sku, name, _ = random.choice(SKUS)
        ref = random.choice(["Sales Order SO-" + str(random.randint(4000, 4999)),
                              "Goods In PO-" + str(random.randint(2000, 2999)),
                              "Transfer T-" + str(random.randint(100, 999))])
        add_audit(sku, name, random.choice([-4, -3, -2, -1, 1, 2, 3, 5]), ref, store_id)

# Add cross-store noise
for _ in range(50):
    sku, name, _ = random.choice(SKUS)
    store_id = random.randint(1, 40)
    ref = random.choice(["Sales Order SO-" + str(random.randint(4000, 4999)),
                          "Goods In PO-" + str(random.randint(2000, 2999)),
                          "Transfer T-" + str(random.randint(100, 999))])
    add_audit(sku, name, random.choice([-4, -3, -2, -1, 1, 2, 3, 5]), ref, store_id)

random.shuffle(audit_rows)

# Write audit trail with Warehouse containing full store names
with open(os.path.join(INPUT_DIR, "AuditTrail_03_07_26.csv"), "w", newline="") as f:
    fields = ["Product ID", "SKU", "Product Name", "Options", "Quantity", "Price",
              "Reference", "Warehouse", "Date", "Movement ID"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(audit_rows)

print(f"Audit trail: {len(audit_rows)} rows")
print(f"Variance files: {len(ALL_STORES - INCOMPLETE_STORES)}")
print("Done.")
