import os
from urllib.parse import urlparse

from pyspark.sql import SparkSession

# Resolve the PostgreSQL JDBC jar relative to this file (spark_jobs/../postgresql-*.jar)
_HERE = os.path.dirname(os.path.abspath(__file__))
_JDBC_JAR = os.path.join(_HERE, "..", "postgresql-42.7.3.jar")


def get_spark(app_name):
    jar_path = os.path.abspath(_JDBC_JAR)
    if not os.path.exists(jar_path):
        raise FileNotFoundError(
            f"PostgreSQL JDBC jar not found at {jar_path}. "
            "Download it from https://jdbc.postgresql.org/ and place it in the repo root."
        )
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.jars", jar_path)
        .getOrCreate()
    )


def get_log_path():
    return os.environ.get("LOG_PATH", "logs/app.json.log")


def get_jdbc_config():
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://fleuris_user:password@localhost/fleuris_db",
    )
    parsed = urlparse(database_url)
    jdbc_url = f"jdbc:postgresql://{parsed.hostname}:{parsed.port or 5432}{parsed.path}"
    properties = {
        "user": parsed.username or "fleuris_user",
        "password": parsed.password or "password",
        "driver": "org.postgresql.Driver",
    }
    return jdbc_url, properties
