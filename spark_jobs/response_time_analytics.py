from pyspark.sql.functions import avg, col, current_timestamp, expr

from utils import get_jdbc_config, get_log_path, get_spark


def main():
    spark = get_spark("FleurisResponseTimeAnalytics")
    log_path = get_log_path()

    logs = spark.read.json(log_path)
    response_times = (
        logs.filter(col("event_type") == "http_request")
        .groupBy("endpoint")
        .agg(
            avg(col("response_time_ms")).alias("avg_response_ms"),
            expr("percentile_approx(response_time_ms, 0.95)").alias("p95_response_ms"),
        )
        .withColumn("last_updated", current_timestamp())
    )

    jdbc_url, properties = get_jdbc_config()
    response_times.write.mode("overwrite").option("truncate", "true").jdbc(
        jdbc_url,
        "analytics_response_times",
        properties=properties,
    )
    spark.stop()


if __name__ == "__main__":
    main()
