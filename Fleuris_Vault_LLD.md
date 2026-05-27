# Fleuris Vault – Low-Level Design (LLD)

## 1. Purpose
Fleuris Vault is a Flask-based digital banking demo that focuses on secure user flows, admin operations, structured observability, and operational analytics. The application is intentionally small enough to reason about end to end, but the design mirrors a production service: it has role-based access control, CSRF protection, audit logging, PostgreSQL persistence, and a batch analytics pipeline driven from JSON logs.

## 2. Technology Stack
- **Backend:** Python 3.12+, Flask 2.3
- **Database:** PostgreSQL through SQLAlchemy ORM and psycopg2
- **Frontend:** Jinja2 templates, HTML, CSS
- **Security:** Werkzeug password hashing, pyotp MFA, qrcode provisioning, custom response headers
- **Logging:** JSON log files written by the Flask app, plus DB-backed security events
- **Analytics:** PySpark jobs that read JSON logs and write summary tables to PostgreSQL
- **Deployment:** Gunicorn behind Nginx on EC2, plus Render support

## 3. System Architecture
### 3.1 Core Layers
- **Application factory:** `app/__init__.py` builds the Flask app, configures extensions, registers blueprints, and installs response headers.
- **Routes:** Request handling is split by concern in `app/routes/` for auth, core banking, admin, security, analytics, transfer, and traffic generation.
- **Services:** Shared logic lives in `app/services/` for auth, security logging, seeding, and transfer behavior.
- **Models:** SQLAlchemy models are centralized in `app/models.py`.
- **Templates:** Jinja templates render all pages and admin dashboards.
- **Static assets:** Styling is in `static/style.css`.

### 3.2 Runtime Data Stores
- **Primary application tables:** `users`, `transactions`, `security_events`
- **Analytics tables:** endpoint popularity, login summary, response time summary, user activity summary, traffic run history
- **Log file:** `logs/app.json.log` stores JSON events for Spark jobs and audit review

## 4. Request and Control Flow
### 4.1 Authentication Flow
1. The login page submits username, password, and optional MFA code.
2. The auth service loads the user from PostgreSQL.
3. Passwords are checked against stored hashes.
4. If MFA is enabled, TOTP is validated before the session is accepted.
5. On success, the session is populated and the failed-login counter is reset.
6. On failure, the attempt is logged and the user may be locked out after repeated failures.

### 4.2 Customer Banking Flow
1. A logged-in customer opens the dashboard.
2. Transfer requests require a session-bound CSRF token.
3. The transfer service validates the recipient, amount, and current balance.
4. The transaction row is written to PostgreSQL and the relevant balances are updated.
5. A structured security event and JSON log entry are emitted.

### 4.3 Admin Operations Flow
1. Admin routes verify the current user’s role before any privileged action.
2. Security pages read from the audit table and the JSON log file.
3. Admin controls can seed demo transactions, lock test users, and clear DB audit events.
4. Analytics actions can run PySpark jobs from the UI, which keeps operators out of the terminal.

## 5. Module Breakdown
### 5.1 App Initialization
- Config loads from environment variables.
- SQLAlchemy is initialized once for the app.
- Structured logging is configured to write JSON events.
- Security headers are applied to every response.
- Blueprints are registered during startup.

### 5.2 Authentication and Session Management
- `login_required()` returns the current session user.
- `generate_csrf_token()` creates a session-bound token for POST requests.
- `require_csrf_token()` blocks missing or mismatched tokens.
- `authenticate_user()` owns password/MFA validation and lockout handling.

### 5.3 Security and Audit Logging
- `log_event()` writes DB audit events and JSON log lines.
- `read_log_lines()` tails the log file for the security log page.
- Access-denied, login-success, login-failed, transfer, MFA, and CSRF events are all captured.

### 5.4 Analytics Module
- The analytics dashboard reads summary rows from PostgreSQL.
- The UI can launch PySpark jobs for endpoint popularity, login analytics, response times, and user activity.
- The jobs read the JSON log file and write aggregated tables back to PostgreSQL.

### 5.5 Traffic Generator
- The traffic generator creates realistic app activity through the Flask test client.
- It produces login, dashboard, transfer, and failure scenarios.
- It records each run in the analytics traffic-run table for traceability.

## 6. Analytics Workflow
### 6.1 Input Source
- The Flask app emits JSON lines into `logs/app.json.log`.
- Only request and event logs that already follow the JSON structure should be fed into Spark.

### 6.2 Batch Jobs
- **Endpoint popularity:** counts request hits per endpoint.
- **Login analytics:** groups login success/failure/lockout/MFA events.
- **Response time analytics:** computes average and p95 latency per endpoint.
- **User activity summary:** counts requests per user and tracks last activity time.

### 6.3 Output Tables
- Each Spark job overwrites the corresponding analytics table in PostgreSQL.
- The analytics dashboard only displays what is already persisted in those tables.
- The traffic-run history is stored separately so admins can tell whether the data source was exercised.

## 7. Deployment Workflow
### 7.1 Local Development
- Configure PostgreSQL locally.
- Set `DATABASE_URL`, `AEGIS_SECRET_KEY`, `LOG_DIR`, and the Spark JDBC jar path.
- Start the Flask app from the repo root.
- Generate traffic and run analytics jobs from the UI to verify the full loop.

### 7.2 EC2 Production Path
1. Provision Ubuntu, PostgreSQL, Nginx, Gunicorn, and Java.
2. Create the database and user, then assign `DATABASE_URL`.
3. Install Python dependencies into the app virtual environment.
4. Copy the systemd and Nginx configs from `ops/`.
5. Place the PostgreSQL JDBC jar where Spark can load it.
6. Start the app service and reverse proxy.
7. Enable Filebeat so JSON logs are forwarded for observability.

### 7.3 Render Path
- Set the build/start commands and environment variables.
- Use PostgreSQL as the managed database.
- Verify the app initializes tables on startup and can write logs to the configured path.

## 8. Pre-AWS Test Plan
Run these checks before deploying to AWS.

### 8.1 Configuration Checks
- Confirm PostgreSQL is reachable.
- Confirm `DATABASE_URL` points to the correct database.
- Confirm `LOG_DIR` exists and is writable.
- Confirm the PostgreSQL JDBC jar exists and is loaded by Spark.

### 8.2 Application Smoke Tests
- Log in as a customer and verify the dashboard loads.
- Submit a transfer and verify the transaction appears in statements.
- Log in as the admin user and verify admin navigation is visible.
- Open the security page and security log page.
- Open the analytics dashboard and confirm it renders without a traceback.

### 8.3 Analytics Tests
- Generate traffic from the UI.
- Run all Spark jobs from the analytics page.
- Confirm the endpoint, login, response time, and user activity panels populate.
- Confirm the traffic run history increments.

### 8.4 Security Tests
- Try a transfer without a CSRF token and confirm it is blocked.
- Try admin pages as a customer and confirm 403 responses.
- Trigger a failed login and confirm audit events are written.
- Verify the security log page can read the JSON log file.

## 9. Deployment Validation Checklist
- Application boots cleanly with no missing environment variables.
- PostgreSQL tables exist and are readable.
- Security log page works against the live log file.
- Analytics jobs run end to end from the UI.
- Nginx can reach Gunicorn.
- Filebeat can tail the JSON log file.
- The JDBC jar is available to Spark jobs.

## 10. Operational Notes
- The analytics dashboard is only as complete as the JSON log history behind it.
- Running the traffic generator is useful before Spark jobs because it creates realistic events.
- If analytics tables are empty, re-run traffic generation first, then rerun the Spark jobs.
- If security pages fail, verify the log path and file permissions before looking at the app code.

## 11. Demo Accounts
- `alex / pass` - customer
- `morgan / pass` - customer
- `taylor / pass` - customer
- `casey / pass` - customer
- `jordan / pass` - customer
- `raghav / 123` - admin

## 12. Key Endpoints
- `/` - home
- `/login`, `/logout`, `/mfa-setup` - authentication
- `/dashboard` - main banking dashboard
- `/transfer` - customer transfer flow
- `/statement`, `/statement/<id>` - statement views
- `/users`, `/admin/users/<id>` - admin user management
- `/security`, `/security-log` - security operations
- `/analytics` - analytics dashboard
- `/traffic-generator` - traffic generation UI

This document is intended to serve as the implementation reference and the pre-deployment test checklist for Fleuris Vault.
