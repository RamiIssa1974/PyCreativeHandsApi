# 🐍 PyCreativeHandsApi

**PyCreativeHandsApi** is a full backend API built with **FastAPI (Python 3.11)** as a modern re-implementation of the original **CreativeHandsCoreApi (.NET Core)**.  
It preserves all existing endpoints so the existing website and clients continue to work seamlessly.

Live demo: [http://py.creativehandsco.com](http://py.creativehandsco.com)

---

## 🚀 Overview

This project is part of the **CreativeHandsProjects** solution and serves as the Python-based REST API for all product, category, and order operations.  
It connects directly to **Microsoft SQL Server** and is fully deployable on **Windows Server 2019** under IIS via reverse proxy.

### ✅ Key Features

- ⚙️  Compatible with existing .NET API endpoints  
- ⚡  Built using **FastAPI** and **SQLAlchemy**
- 🗄️  Connects to **Microsoft SQL Server** via **pyodbc**
- 🧩  Uses `.env` configuration for flexible deployment
- 🧠  Designed for future extension (MongoDB / Redis providers)
- 💻  Hosted on **Windows Server 2019** with **IIS** + **Uvicorn**
- 📦  Easy to run locally using virtual environment (`venv`)

---

## 🧠 Tech Stack

| Layer | Technology |
|-------|-------------|
| Language | Python 3.11 |
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | Microsoft SQL Server |
| Driver | ODBC Driver 17 for SQL Server |
| Hosting | IIS (Reverse Proxy) + Uvicorn |
| OS | Windows Server 2019 |
| Env Config | python-dotenv |

---

## 🗂️ Project Structure
PyCreativeHandsApi/
│
├── app/
│ ├── main.py # FastAPI entry point
│ ├── routers/ # Controllers (Products, Orders, etc.)
│ ├── repositories/ # Data access logic (SQLAlchemy)
│ ├── models_sql/ # ORM model definitions
│ ├── schemas/ # Pydantic models for validation
│ └── db/ # DB session and connection helpers
│
├── .env # Environment variables (not committed)
├── .gitignore
├── requirements.txt
└── README.md

---

## ⚙️ Environment Variables (`.env`)
APP_NAME=PyCreativeHandsApi
ENV=prod

SQLSERVER_HOST=localhost
SQLSERVER_DB=Market
SQLSERVER_USER=your_user
SQLSERVER_PASSWORD=your_password
SQL_ODBC_DRIVER=ODBC Driver 17 for SQL Server
SQL_TRUST_CERT=true

---

## 🏃 How to Run (Local)

```bash
# 1. Create a virtual environment
py -3.11 -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API
uvicorn app.main:app --host 127.0.0.1 --port 9000

# 4. Visit Swagger UI
http://127.0.0.1:9000/docs
🌐 Deployment Notes
Running under IIS (Windows Server 2019)

API runs with Uvicorn on 127.0.0.1:9000

IIS handles public requests via Application Request Routing (ARR)

Subdomain: py.creativehandsco.com

Reverse proxy rule forwards all traffic to Uvicorn

Windows Service

The backend can run as a persistent Windows service using NSSM:
nssm install PyCreativeHandsApi "C:\Apps\PyCreativeHandsApi\.venv\Scripts\uvicorn.exe" app.main:app --host 127.0.0.1 --port 9000 --workers 2
🔮 Future Plans

Add optional Redis or MongoDB data providers

Add JWT authentication and user roles

Integrate caching layer for product endpoints

Dockerfile for Linux deployment
📚 Related Projects
Project	Description
CreativeHandsCoreApi
	Original .NET Core version
CreativeHandsWeb
	Frontend website
PyCreativeHandsApi
	Python 3.11 version (FastAPI)
✨ Author

Rami Issa
📍 Software Engineer & Backend Developer
🔗 creativehandsco.com/Rami/RamiIssa.html

💼 GitHub – RamiIssa1974

🧾 License

This project is part of the CreativeHandsProjects suite.
All rights reserved © Creative Hands Co.








