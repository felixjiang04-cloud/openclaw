# Quick Start (5 minutes)

## If you already have a Google Sheet set up

### 1. Install gog
```bash
# macOS
brew install steipete/tap/gog

# Linux/WSL
curl -L https://github.com/steipete/gogcli/releases/download/v0.9.0/gogcli_0.9.0_linux_amd64.tar.gz -o gogcli.tar.gz
tar -xzf gogcli.tar.gz -C /tmp && sudo install -m 0755 /tmp/gog /usr/local/bin/gog
```

### 2. Authenticate
```bash
gog auth add your-email@gmail.com --manual --services sheets
# Approve in browser, copy the redirect URL back to terminal
```

### 3. Update the script
Edit `inventory.py`:
```python
SHEET_ID = "your-sheet-id"      # From Google Sheet URL
ACCOUNT = "your-email@gmail.com"
```

### 4. Set passphrase
```bash
export GOG_KEYRING_PASSWORD="your-keyring-passphrase"
```

### 5. Test it
```bash
python inventory.py list
```

Done! Now use it:

```bash
python inventory.py use 2 "chicken breast"
python inventory.py check
python inventory.py recv 10 "oat milk"
```

---

## If you don't have a Google Sheet yet

1. **Copy the template sheet** → [OpenClaw Inventory Template](https://docs.google.com/spreadsheets/d/1JWY96k0YIkPmCICpNienKmD5V1kMTzcjiV5gt-E0LOc)
   - Click "File" → "Make a copy"
   - Rename it to "My Business Inventory"

2. **Follow steps 1-5 above** (use your copied sheet's ID)

3. **Add your items** in the "inventory" tab (see README for structure)

---

## Common Issues

**"No JSON in output"** → Run `export GOG_KEYRING_PASSWORD="your-passphrase"` first

**"Item not found"** → Make sure `active` is `TRUE` in the sheet

**"No gog command found"** → Re-run the install step above

---

## Next Steps

- Add more items to the inventory sheet
- Set up OpenClaw integration for Telegram bot (see Phase 2 in README)
- Invite staff to the sheet so they can log changes

Questions? Check the full README.md
