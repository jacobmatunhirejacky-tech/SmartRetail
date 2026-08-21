# SmartRetail

A resilient, offline-first Point of Sale (POS) and inventory management platform designed for retail environments with intermittent network connectivity. It utilizes a **dual-database architecture** combining a local SQLite database for instantaneous, zero-downtime offline transactions and a cloud-hosted PostgreSQL database (Neon) for centralized sales tracking and synchronization.

---

## Architecture Overview

SmartRetail ensures continuous checkout lane availability regardless of network health:

* **Local Database (Edge):** Embedded SQLite (`local_sales.db`) handles local sales recording, receipt logging, and cash register tasks without network latency.
* **Central Database (Core):** Managed cloud PostgreSQL (Neon) aggregates sales records from multiple retail endpoints and acts as the central data store.
* **Sync Layer:** Syncs local transactional records to the remote database when network connectivity is available, supporting continuous offline-first retail operations.

```text
[ POS Web Client (Flask + HTML/CSS) ]
                 │
          (Reads / Writes)
                 ▼
     [ Local SQLite (Edge DB) ]
                 │
        (Synchronization)
                 ▼
   [ Central PostgreSQL (Neon DB) ]
```

---

## Features

* **Zero-Downtime Offline Checkout:** Perform sales and record transactions locally even when completely offline.
* **Dual-Database Syncing:** Seamlessly reconcile local offline sales records with the remote PostgreSQL central ledger.
* **Web-Based POS Interface:** Lightweight frontend built with Flask templates and styled with custom CSS.
* **Transaction Resilience:** Local database persistence ensures no transaction is lost during network dropouts.

---

## Tech Stack

* **Backend:** Python 3.11+ / Flask
* **Local Edge Database:** SQLite 3 (`local_sales.db`)
* **Central Cloud Database:** PostgreSQL (Neon Serverless)
* **Database Drivers:** `psycopg2-binary`, standard library `sqlite3`
* **Frontend:** HTML5, CSS3, Jinja2 Templates

---

## Project Structure

```text
Smart_retail/
├── static/
│   └── style.css            # Custom POS styling
├── templates/
│   └── index.html           # Main POS interface
├── app.py                   # Flask server & route endpoints
├── database.py              # Dual-database connection & sync logic
├── local_sales.db           # Local SQLite store (auto-generated)
├── .env.example             # Example environment configuration
├── .gitignore               # Git exclusions (credentials, venv, DB files)
└── requirements.txt         # Project dependencies
```

---

## Getting Started

### 1. Clone the Repository
```powershell
git clone https://github.com/jacobmatunhirejacky-tech/SmartRetail.git
cd SmartRetail
```

### 2. Set Up Virtual Environment
On Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install flask psycopg2-binary python-dotenv
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (never commit this file to Git):
```env
NEON_DATABASE_URL=postgresql://<username>:<password>@<host>/<database>?sslmode=require
LOCAL_DB_NAME=local_sales.db
```

### 5. Initialize the Database
Run the initialization routine to set up the local tables:
```powershell
python -c "import database; database.init_db()"
```

### 6. Run the Application
```powershell
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

