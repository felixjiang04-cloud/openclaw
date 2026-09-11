import subprocess
import json
import sys
import os
from datetime import datetime

SHEET_ID = "1JWY96k0YIkPmCICpNienKmD5V1kMTzcjiV5gt-E0LOc"
ACCOUNT = "felixjiangagent1@gmail.com"
PASSPHRASE = os.environ.get("GOG_PASS", "")

def run_gog(args, input_text=None):
    """Run a gog command, piping passphrase twice (keyring prompts twice)."""
    pw = (PASSPHRASE + "\n") * 2
    result = subprocess.run(
        ["gog"] + args + ["--account", ACCOUNT],
        input=pw + (input_text or ""),
        capture_output=True, text=True
    )
    return result

def gog_get(range_str):
    result = run_gog(["sheets", "get", "--json", SHEET_ID, range_str])
    if result.returncode != 0:
        print(f"Error reading sheet: {result.stderr}")
        return []
    # Strip any passphrase prompt text before the JSON
    stdout = result.stdout
    json_start = stdout.find("{")
    if json_start == -1:
        print(f"No JSON in output: {stdout[:200]}")
        return []
    data = json.loads(stdout[json_start:])
    return data.get("values", [])

def gog_update(range_str, row_values):
    pipe_str = "|".join(str(v) for v in row_values)
    result = run_gog(["sheets", "update", SHEET_ID, range_str, pipe_str])
    if result.returncode != 0:
        print(f"Error writing sheet: {result.stderr}")
        return False
    return True

def gog_append(range_str, row_values):
    pipe_str = "|".join(str(v) for v in row_values)
    result = run_gog(["sheets", "append", SHEET_ID, range_str, pipe_str])
    if result.returncode != 0:
        print(f"Error appending to sheet: {result.stderr}")
        return False
    return True

def get_inventory():
    rows = gog_get("inventory!A1:O")
    if len(rows) < 2:
        return []
    headers = rows[0]
    items = []
    for row in rows[1:]:
        row += [""] * (len(headers) - len(row))
        item = dict(zip(headers, row))
        if item.get("active", "").upper() == "TRUE":
            items.append(item)
    return items

def find_item(query):
    items = get_inventory()
    query_lower = query.lower().strip()
    exact = [i for i in items if i["name"].lower() == query_lower or i["name_fr"].lower() == query_lower]
    if exact:
        return exact
    partial = [i for i in items if query_lower in i["name"].lower() or query_lower in i["name_fr"].lower()]
    if partial:
        return partial
    words = query_lower.split()
    fuzzy = [i for i in items if all(w in i["name"].lower() for w in words)]
    return fuzzy

def find_item_row(item_id):
    rows = gog_get("inventory!A:A")
    for i, row in enumerate(rows):
        if row and row[0] == item_id:
            return i + 1
    return None

def check_stock(query=None):
    if query:
        matches = find_item(query)
        for m in matches:
            status = "LOW" if float(m["current_stock"]) <= float(m["reorder_point"]) else "OK"
            print(f"  {m['name']}: {m['current_stock']} {m['unit']} [{status}]")
        if not matches:
            print(f"  No item matching '{query}'")
        return matches
    else:
        items = get_inventory()
        low = [i for i in items if float(i["current_stock"]) <= float(i["reorder_point"])]
        if low:
            print("Low stock items:")
            for i in low:
                print(f"  ⚠ {i['name']}: {i['current_stock']} {i['unit']} (reorder at {i['reorder_point']})")
        else:
            print("  All items above reorder point.")
        return low

def log_transaction(item_id, item_name, tx_type, quantity, logged_by, notes=""):
    row_num = find_item_row(item_id)
    if not row_num:
        print(f"Item {item_id} not found")
        return None

    rows = gog_get(f"inventory!A{row_num}:O{row_num}")
    headers = gog_get("inventory!A1:O1")[0]
    item = dict(zip(headers, rows[0] + [""] * (len(headers) - len(rows[0]))))

    stock_before = float(item["current_stock"])
    reorder_point = float(item["reorder_point"])

    if tx_type == "received":
        stock_after = stock_before + quantity
    elif tx_type == "counted":
        stock_after = quantity
    else:
        stock_after = stock_before - quantity
        if stock_after < 0:
            print(f"  Warning: stock went negative, setting to 0")
            stock_after = 0

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tx_count = len(gog_get("transactions!A:A"))
    tx_id = f"tx-{datetime.now().strftime('%Y%m%d')}-{tx_count:03d}"

    tx_row = [tx_id, now, item_id, item_name, tx_type, quantity,
              stock_before, stock_after, logged_by, notes]
    gog_append("transactions!A:J", tx_row)

    gog_update(f"inventory!G{row_num}", [stock_after])

    alert = stock_after <= reorder_point and stock_before > reorder_point

    print(f"  ✅ {tx_type}: {quantity} {item['unit']} {item_name}")
    print(f"  Stock: {stock_before} → {stock_after} {item['unit']}")
    if alert:
        print(f"  ⚠️ LOW STOCK ALERT: {item_name} is at {stock_after} {item['unit']} (reorder point: {reorder_point})")

    return {"tx_id": tx_id, "stock_after": stock_after, "alert": alert}

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python inventory.py check [item]     — check stock")
        print("  python inventory.py use <qty> <item>  — log usage")
        print("  python inventory.py sell <qty> <item> — log sale")
        print("  python inventory.py recv <qty> <item> — log receipt")
        print("  python inventory.py waste <qty> <item> — log waste")
        print("  python inventory.py list              — list all items")
        return

    cmd = sys.argv[1]

    if cmd == "check":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        check_stock(query)
    elif cmd == "list":
        items = get_inventory()
        for i in items:
            print(f"  {i['item_id']:20s} {i['name']:20s} {i['current_stock']:>8s} {i['unit']}")
    elif cmd in ("use", "sell", "recv", "waste"):
        type_map = {"use": "used", "sell": "sold", "recv": "received", "waste": "wasted"}
        qty = float(sys.argv[2])
        query = " ".join(sys.argv[3:])
        matches = find_item(query)
        if len(matches) == 0:
            print(f"No item matching '{query}'")
        elif len(matches) > 1:
            print("Multiple matches:")
            for m in matches:
                print(f"  {m['item_id']}: {m['name']} ({m['current_stock']} {m['unit']})")
        else:
            item = matches[0]
            log_transaction(item["item_id"], item["name"], type_map[cmd], qty, "felix")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
