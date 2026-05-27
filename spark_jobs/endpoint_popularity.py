from pyspark.sql.functions import col, count, current_timestamp

from utils import get_jdbc_config, get_log_path, get_spark


def main():
    spark = get_spark("FleurisEndpointPopularity")
    log_path = get_log_path()

    logs = spark.read.json(log_path)
    endpoint_hits = (
        logs.filter(col("event_type") == "http_request")
        .groupBy("endpoint")
        .agg(count("endpoint").alias("total_hits"))
        .withColumn("last_updated", current_timestamp())
    )

    jdbc_url, properties = get_jdbc_config()
    endpoint_hits.write.mode("overwrite").option("truncate", "true").jdbc(
        jdbc_url,
        "analytics_endpoint_popularity",
        properties=properties,
    )
    spark.stop()


if __name__ == "__main__":
    main()
