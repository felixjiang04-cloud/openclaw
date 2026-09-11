# OpenClaw Inventory Management

A Python CLI tool for managing small business inventory via Google Sheets integration. Built for restaurants, depanneurs, coffee shops, bakeries, and bars using OpenClaw automation.

## Features

- **Stock tracking** — Check current inventory levels across all items
- **Transaction logging** — Log usage, sales, received shipments, and waste
- **Low-stock alerts** — Automatic warnings when items fall below reorder points
- **Fuzzy matching** — Find items by partial name, English or French
- **Bilingual support** — Item names in both English and French
- **Google Sheets backend** — All data persists in a shared spreadsheet
- **Audit trail** — Transaction history with timestamps and who logged each change

## Setup

### Prerequisites

- Python 3.8+
- `gog` CLI installed ([download](https://github.com/steipete/gogcli/releases))
- Google account with Google Sheets access
- OpenClaw instance (optional, for Telegram integration)

### 1. Install `gog`

On macOS:
```bash
brew install steipete/tap/gog
```

On Linux/WSL:
```bash
curl -L https://github.com/steipete/gogcli/releases/download/v0.9.0/gogcli_0.9.0_linux_amd64.tar.gz -o gogcli.tar.gz
tar -xzf gogcli.tar.gz -C /tmp
sudo install -m 0755 /tmp/gog /usr/local/bin/gog
```

On Windows (PowerShell):
```powershell
# Download the Windows binary from:
# https://github.com/steipete/gogcli/releases/download/v0.9.0/gogcli_0.9.0_windows_amd64.exe
# And add it to your PATH
```

### 2. Authenticate with Google

```bash
gog auth add your-email@gmail.com --manual --services sheets
```

In a browser, approve the Google Sheets scope. Copy the redirect URL from the browser (after it fails to load) and paste it back in the terminal within 60 seconds.

### 3. Create Google Sheet

Create a Google Sheet with these tabs (in order):
- **config** — Settings for your business
- **inventory** — Item master data
- **transactions** — Audit log of all stock changes

Or copy this template: [OpenClaw Inventory Template](https://docs.google.com/spreadsheets/d/1JWY96k0YIkPmCICpNienKmD5V1kMTzcjiV5gt-E0LOc)

### 4. Update Script Configuration

Edit `inventory.py` and replace these constants:

```python
SHEET_ID = "your-sheet-id-here"  # From the sheet URL
ACCOUNT = "your-email@gmail.com"
```

Get your sheet ID from the URL: `docs.google.com/spreadsheets/d/{SHEET_ID}/edit`

### 5. Set Environment Variables

```bash
# Set keyring passphrase (one-time or per session)
export GOG_KEYRING_PASSWORD="your-keyring-passphrase"

# Optional: Store for all sessions in ~/.bashrc
echo 'export GOG_KEYRING_PASSWORD="your-passphrase"' >> ~/.bashrc
```

## Usage

### Check stock levels

```bash
# Check all items
python inventory.py check

# Check one item
python inventory.py check chicken
python inventory.py check lait

# Check French names too
python inventory.py check "lait d'avoine"
```

### List all items

```bash
python inventory.py list
```

### Log stock changes

```bash
# Usage (item consumed)
python inventory.py use 2.5 "chicken breast"

# Sale (item sold to customer)
python inventory.py sell 5 "oat milk"

# Receipt (item received from supplier)
python inventory.py recv 24 "coke"

# Waste (item spoiled/discarded)
python inventory.py waste 1.5 "romaine lettuce"
```

### View low-stock items

Low-stock alerts appear automatically when items fall below their reorder point:

```
python inventory.py check

Low stock items:
  ⚠ Chicken Breast: 4.5 kg (reorder at 5.0)
  ⚠ Oat Milk: 1 units (reorder at 2)
```

## Google Sheets Structure

### Config Tab

| Key | Value |
|---|---|
| business_name | G15 Test Restaurant |
| business_type | restaurant |
| language | en |
| timezone | America/Montreal |
| currency | CAD |

### Inventory Tab

| Column | Type | Example |
|---|---|---|
| item_id | Text | chicken-breast |
| name | Text | Chicken Breast |
| name_fr | Text | Poitrine de poulet |
| category | Text | Proteins |
| subcategory | Text | Poultry |
| unit | Text | kg |
| current_stock | Number | 12.5 |
| reorder_point | Number | 5 |
| reorder_qty | Number | 20 |
| supplier | Text | Local Farm |
| cost_per_unit | Currency | 8.50 |
| expiry_days | Number | 0 |
| active | Boolean | TRUE |
| created_at | Date | 2026-04-29 |
| created_by | Text | felix |

### Transactions Tab

| Column | Type |
|---|---|
| tx_id | Text (auto) |
| timestamp | DateTime (auto) |
| item_id | Text |
| item_name | Text |
| tx_type | Text (used/sold/received/wasted) |
| quantity | Number |
| stock_before | Number |
| stock_after | Number |
| logged_by | Text |
| notes | Text |

## Troubleshooting

### "No JSON in output"
The keyring passphrase is being prompted but not supplied. Set:
```bash
export GOG_KEYRING_PASSWORD="your-passphrase"
```

### "Item not found"
Ensure the item is in the inventory tab and `active` is `TRUE`.

### "Multiple matches"
Be more specific with the item name, or use the full `item_id`:
```bash
python inventory.py use 2 chicken-breast
```

### "No TTY available for keyring file backend password prompt"
Same as "No JSON" — you need `GOG_KEYRING_PASSWORD` set.

### Sheet not updating
Check that the sheet ID and account email are correct in `inventory.py`.

## Phase 2: OpenClaw Integration

To wire this into OpenClaw Telegram bot:

1. Export functions as OpenClaw tools/plugins
2. Create a skill SKILL.md that wraps these functions
3. Add to OpenClaw config under `[tools]`
4. Staff can then log inventory via Telegram: "used 2kg chicken"
5. Bot sends low-stock alerts to a Telegram group automatically

[See Phase 2 design doc](./PHASE2.md) for full implementation.

## License

MIT

## Author

G15 Systems — AI automation for small businesses
