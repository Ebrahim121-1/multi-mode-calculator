## Multi‑Mode Calculator (Flask)

### Overview
Web calculator that switches between modes:
- **Regular**: basic arithmetic
- **Scientific**: functions like `sin`, `cos`, `tan`, `sqrt`, `log10`, `ln`, `exp`, `x^y`, `abs`, `n!`, constants `π`, `e`
- **Converter**: units (length, mass, volume, temperature), currency (static demo rates), data size (SI and IEC)

Includes:
- **Keyboard support**: type digits/operators; Enter/= to evaluate; Backspace to delete; Esc/C/Delete to clear
- **Touch/pointer**: buttons respond to click and press
- **Back key**: tap = backspace; long‑press ≈0.6s = clear expression
- **History drawer**: locally stored (localStorage) with Use, Edit, Delete, Clear‑all

### Quick start (Windows PowerShell)
```powershell
cd D:\current
python -m venv .venv
.# If policy blocks activation, run once: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

### Quick start (macOS/Linux)
```bash
cd /path/to/current
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Usage tips
- Switch modes with the tabs at the top right
- Scientific: you can type function names (e.g., `sin(30)`), `^` works as power
- Converters: pick category/units or currencies, enter a value, click Convert; results appear in a side box
- History: click the ≡ button → Use to load, Edit to modify and re‑evaluate, Delete/Clear to remove

### Keyboard shortcuts
- Digits/operators: `0-9 . + - * / % ^ ( ) ,`
- Functions: start typing letters (e.g., `sin`, `cos`, `tan`, `log10`, `ln`, `exp`)
- Evaluate: `Enter` or `=`
- Backspace: `Backspace`
- Clear: `Esc`, `Delete`, or `C`

### Endpoints (for reference)
- `POST /calc` → `{ expression }` → `{ ok, result }` using a safe math sandbox
- `POST /convert/unit` → `{ category, from, to, value }` → `{ ok, result }`
- `POST /convert/currency` → `{ from, to, value }` → `{ ok, result }` (static demo rates)
- `POST /convert/datasize` → `{ from, to, value }` → `{ ok, result }`

### Customize
- **Live currency rates**: replace the static table in `app.py` with a rates API and cache results
- **More units**: extend the unit maps in `app.py`
- **Styling**: edit `templates/index.html` CSS (colors, sizes, shapes)

### Project structure
```
current/
  app.py                 # Flask app + endpoints
  requirements.txt       # Dependencies
  templates/
    index.html           # UI (modes, keypad, converters, history)
  README.md              # This file
```

### Notes
- Currency uses demo rates for offline usage; do not rely on them for real transactions
- The evaluator allows only whitelisted math functions/constants

### Deploying (basic)
- Any WSGI host works. Example (Linux):
```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```


