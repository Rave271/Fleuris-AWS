from pyspark.sql.functions import col, count, current_timestamp, max as spark_max

from utils import get_jdbc_config, get_log_path, get_spark


def main():
    spark = get_spark("FleurisUserActivity")
    log_path = get_log_path()

    logs = spark.read.json(log_path)
    activity = (
        logs.filter(col("event_type") == "http_request")
        .filter(col("username").isNotNull())
        .groupBy("username", "user_id")
        .agg(
            count("endpoint").alias("total_requests"),
            spark_max(col("timestamp").cast("timestamp")).alias("last_seen"),
        )
        .withColumn("last_updated", current_timestamp())
    )

    jdbc_url, properties = get_jdbc_config()
    activity.write.mode("overwrite").option("truncate", "true").jdbc(
        jdbc_url,
        "analytics_user_activity",
        properties=properties,
    )
    spark.stop()


if __name__ == "__main__":
    main()
