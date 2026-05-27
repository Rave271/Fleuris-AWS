# AWS Deployment Guide (Single EC2)

This guide deploys Fleuris Vault on one Ubuntu EC2 instance with PostgreSQL, Gunicorn, Nginx, Filebeat, Elasticsearch, Kibana, and PySpark.

## 1. EC2 Basics

- Recommended: Ubuntu 22.04, t3.small or higher
- Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 5601 (Kibana), 9200 (Elasticsearch)

## 2. System Packages

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx postgresql postgresql-contrib default-jre
```

## 3. PostgreSQL Setup

```bash
sudo -u postgres psql
CREATE USER fleuris_user WITH PASSWORD 'password';
CREATE DATABASE fleuris_db OWNER fleuris_user;
\q
```

Set the app connection string:

```bash
export DATABASE_URL=postgresql://fleuris_user:password@localhost/fleuris_db
```

## 4. App Setup

```bash
cd /opt
sudo git clone <your repo> fleuris-vault
cd fleuris-vault/src
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a production env file:

```bash
cat <<EOF > .env
AEGIS_SECRET_KEY=$(python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)
DATABASE_URL=postgresql://fleuris_user:password@localhost/fleuris_db
LOG_DIR=/var/log/fleuris
EOF

sudo mkdir -p /var/log/fleuris
sudo chown www-data:www-data /var/log/fleuris
```

## 5. Gunicorn Systemd Service

Copy the service file:

```bash
sudo cp /opt/fleuris-vault/ops/gunicorn/fleuris_vault.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fleuris_vault
sudo systemctl start fleuris_vault
sudo systemctl status fleuris_vault
```

## 6. Nginx Reverse Proxy

```bash
sudo cp /opt/fleuris-vault/ops/nginx/fleuris_vault.conf /etc/nginx/sites-available/fleuris_vault
sudo ln -s /etc/nginx/sites-available/fleuris_vault /etc/nginx/sites-enabled/fleuris_vault
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Elasticsearch + Kibana

```bash
sudo apt install -y elasticsearch kibana
sudo systemctl enable elasticsearch kibana
sudo systemctl start elasticsearch kibana
```

Check services:

- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601

## 8. Filebeat

```bash
sudo apt install -y filebeat
sudo cp /opt/fleuris-vault/ops/filebeat/filebeat.yml /etc/filebeat/filebeat.yml
sudo systemctl enable filebeat
sudo systemctl start filebeat
```

## 9. PySpark Jobs

Download the PostgreSQL JDBC driver:

```bash
sudo mkdir -p /opt/fleuris-vault/ops/jars
sudo wget -O /opt/fleuris-vault/ops/jars/postgresql.jar https://jdbc.postgresql.org/download/postgresql-42.7.3.jar
```

```bash
cd /opt/fleuris-vault/spark_jobs
export DATABASE_URL=postgresql://fleuris_user:password@localhost/fleuris_db
export LOG_PATH=/var/log/fleuris/app.json.log
export SPARK_CLASSPATH=/opt/fleuris-vault/ops/jars/postgresql.jar
python3 endpoint_popularity.py
python3 login_analytics.py
python3 response_time_analytics.py
python3 user_activity_summary.py
```

## 10. Kibana Dashboards

Use the starter dashboard notes in ops/kibana/README.md to create visualizations:

- Request volume
- Login trends
- Endpoint popularity
- HTTP status distribution
- Response time trends
- Transfer activity

## 11. Service Commands

```bash
sudo systemctl restart fleuris_vault
sudo systemctl restart nginx
sudo systemctl restart postgresql
sudo systemctl restart elasticsearch
sudo systemctl restart kibana
sudo systemctl restart filebeat
```
