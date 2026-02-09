# Demo Instructions

## Quick Start (2–3 minute flow)

### 1. Start Backend

```bash
cd backend
.\venv\Scripts\Activate.ps1   # or source venv/bin/activate on Linux/Mac
python manage.py runserver
```

### 2. Start Web Frontend

```bash
cd web-frontend
npm run dev
```

Open http://localhost:5173

### 3. Upload CSV (Web)

1. Click "Browse" or drag a CSV file
2. Click "Upload"
3. Select the uploaded dataset from the History sidebar
4. View summary cards, charts (bar, line, pie), and data table
5. Click "Download PDF Report" to generate PDF

### 4. Start Desktop Frontend

```bash
cd desktop-frontend
pip install PyQt5 matplotlib requests pandas
python main.py
```

### 5. Upload CSV (Desktop)

1. File → Upload CSV
2. Browse and select `sample_equipment_data.csv`
3. Click Upload
4. Select dataset from toolbar dropdown
5. View tabs: Summary Stats, Data Table, Charts
6. Click "Generate PDF" and save file

### 6. History Feature

- Web: History sidebar shows last 5 datasets; click to switch
- Desktop: View History menu lists datasets; File → Upload adds new
- When 6th dataset is uploaded, oldest is auto-deleted

## Sample CSV

Use `sample_equipment_data.csv` in the project root. Columns: Equipment Name, Type, Flowrate, Pressure, Temperature.
