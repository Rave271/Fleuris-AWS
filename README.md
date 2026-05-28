# Fleuris Vault

![Fleuris Vault Banner](https://img.shields.io/badge/Architecture-Cloud%20Native-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)

Fleuris Vault is a full-stack, cloud-native digital banking platform designed to demonstrate modern software architecture, secure transactional flows, and integrated data pipelines. It bridges the gap between secure web applications, real-time observability, and big data batch processing.

## 🚀 Key Features

* **Secure Core Banking:** Atomic PostgreSQL transactions ensuring absolute financial consistency during transfers, with dynamic balance calculations and CSV statement exports.
* **Zero-Trust Security:** Built-in CSRF protection, mathematical password hashing, TOTP Multi-Factor Authentication (MFA), and automatic brute-force lockout mechanisms.
* **Dual-Write Telemetry:** Every critical action generates a structured relational database audit log *and* a flat JSON telemetry log simultaneously.
* **Real-Time Observability (ELK):** Integrated Logstash pipeline that tails JSON application logs and ships them to Elasticsearch for live Kibana visualization.
* **Big Data Analytics (PySpark):** On-demand Apache PySpark batch jobs that ingest raw JSON logs, compute complex aggregations (e.g., p95 latency), and write back to PostgreSQL via JDBC.
* **Brutalist UI:** A high-contrast, strictly monochrome "Neo-Brutalist" design system built with vanilla CSS, prioritizing data density and functional performance over bloated frameworks.

---

## 🏗️ Architecture & Tech Stack

Fleuris Vault is designed for single-node deployment (e.g., AWS EC2 `t3.large`), managed entirely via robust Linux `systemd` daemons.

* **Backend:** Python 3.12, Flask 2.3, Gunicorn
* **Database:** PostgreSQL 16, SQLAlchemy 2.0
* **Data Engine:** Apache PySpark 3.5.1
* **Observability:** Elasticsearch, Logstash, Kibana (7.17.4)
* **Web Server:** Nginx (Reverse Proxy)
* **Frontend:** Jinja2, HTML5, Vanilla CSS, Chart.js

---

## 🛡️ Security Implementation

Fleuris Vault adheres to strict OWASP guidelines:
1. **Perimeter Defense:** Nginx absorbs slow-connection attacks and buffers payloads before they reach the Python WSGI server.
2. **Session Integrity:** Cryptographically secure, session-bound CSRF tokens are enforced on all state-changing `POST` requests.
3. **MFA Enforcement:** `pyotp` provides Time-Based One-Time Passwords. If an account enables MFA, the system explicitly blocks authentication without a valid TOTP code.

---

## 📊 The Data Pipeline

The application treats data engineering as a first-class citizen, separating transactional data from analytical data:

1. **Transactional Data:** Money movement goes straight into PostgreSQL for strict ACID compliance.
2. **Audit Telemetry:** Application events are emitted as JSON lines to `logs/app.json.log`.
3. **Batch Processing:** When triggered, PySpark reads the JSON lake, executes map-reduce style aggregations, explicitly casts strict types, and writes the summarized intelligence back to PostgreSQL analytics tables.

---

## 💻 Local Development Setup

### 1. Prerequisites
* Python 3.12+
* PostgreSQL 16
* Java 17 (Required for PySpark)
* PostgreSQL JDBC Driver

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
FLASK_APP=src.app:create_app
FLASK_ENV=development
DATABASE_URL=postgresql://user:password@localhost/fleuris_db
AEGIS_SECRET_KEY=your_secure_random_key_here
LOG_DIR=./logs
```

### 3. Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Database Seeding
```bash
flask shell
>>> from src.app.extensions import db
>>> from src.app.services.seed import seed_users
>>> db.create_all()
>>> seed_users()
>>> exit()
```

### 5. Running the Application
```bash
flask run --port=5000
```
* **Admin Login:** `raghav` / `fleuris_secure_pass`
* **Customer Login:** `alex` / `fleuris_secure_pass`

---

## ☁️ Production Deployment (AWS)

Fleuris Vault is designed to be deployed behind Nginx and Gunicorn on Ubuntu 24.04 LTS. All necessary systemd service files, logstash configurations, and Nginx reverse-proxy blocks are located in the `ops/` directory.

---
*Disclaimer: Fleuris Vault is an architectural demonstration platform. Do not use it to store real financial assets.*
