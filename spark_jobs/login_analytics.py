from pyspark.sql.functions import col, count, current_timestamp

from utils import get_jdbc_config, get_log_path, get_spark


def main():
    spark = get_spark("FleurisLoginAnalytics")
    log_path = get_log_path()

    logs = spark.read.json(log_path)
    logins = (
        logs.filter(col("event_type").isin(["LOGIN_SUCCESS", "LOGIN_FAILED", "LOGIN_LOCKED", "MFA_FAILED"]))
        .groupBy("event_type")
        .agg(count("event_type").alias("total_count"))
        .withColumn("last_updated", current_timestamp())
    )

    jdbc_url, properties = get_jdbc_config()
    logins.write.mode("overwrite").option("truncate", "true").jdbc(
        jdbc_url,
        "analytics_login_summary",
        properties=properties,
    )
    spark.stop()


if __name__ == "__main__":
    main()
