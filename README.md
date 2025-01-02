# stock_analyzer
Analyzing price changes of Turkish stocks in dollar terms.

## Clone:
```bash
git clone https://github.com/vakkaskarakurt/stock_analyzer
```

## Creating Environment:
```bash
python -m venv stockenv
```

## Activate Environment:
### On Windows:
If you encounter an error about script execution, run the following command in PowerShell (with Administrator privileges):
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
Then, activate the environment:
```bash
stockenv\Scripts\activate
```

### On macOS/Linux:
```bash
source stockenv/bin/activate
```

## Installing Requirements:
```bash
pip install -r requirements.txt
```

## Run Program:
```bash
python main.py
```
