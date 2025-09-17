from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
import os, sys
from pathlib import Path

# Try to load configuration from YAML, fallback to defaults
try:
    # Add parent directory to path to import config_loader
    sys.path.append("/opt")
    import yaml
    
    # Load config.yml if available
    config_path = "/opt/config.yml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        bootstrap = config.get('kafka', {}).get('bootstrap_servers', "kafka-1:9092,kafka-2:9092,kafka-3:9092")
        checkpoint_root = config.get('storage', {}).get('checkpoint_root', "/checkpoints") + "/streaming_etl"
        delta_root = config.get('storage', {}).get('datalake_root', "/datalake")
        clickstream_topic = config.get('topics', {}).get('clickstream', "clickstream")
        iot_topic = config.get('topics', {}).get('iot', "iot")
        
        print(f"✅ Loaded configuration from {config_path}")
    else:
        raise FileNotFoundError("config.yml not found")
        
except Exception as e:
    print(f"⚠️  Failed to load configuration ({e}), using defaults")
    bootstrap = "kafka-1:9092,kafka-2:9092,kafka-3:9092"
    checkpoint_root = "/checkpoints/streaming_etl"
    delta_root = "/datalake"
    clickstream_topic = "clickstream"
    iot_topic = "iot"


spark = (SparkSession.builder
.appName("MiniCluster-Streaming-ETL")
.getOrCreate())


spark.sparkContext.setLogLevel("WARN")

# --------- Schemas ---------
click_schema = StructType([
StructField("event_id", StringType()),
StructField("user_id", StringType()),
StructField("url", StringType()),
StructField("referrer", StringType()),
StructField("ua", StringType()),
StructField("session_id", StringType()),  # Added missing field
StructField("ts", StringType()), # ISO8601
])


iot_schema = StructType([
StructField("device_id", StringType()),
StructField("site", StringType()),
StructField("temp_c", DoubleType()),
StructField("humidity", DoubleType()),
StructField("battery", DoubleType()),
StructField("signal_strength", IntegerType()),  # Added missing field
StructField("ts", StringType()), # ISO8601
])


# --------- Clickstream ---------
raw_click = (spark.readStream
.format("kafka")
.option("kafka.bootstrap.servers", bootstrap)
.option("subscribe", clickstream_topic)
.option("startingOffsets", "earliest")
.load())


click = (raw_click
.selectExpr("CAST(key AS STRING) AS k", "CAST(value AS STRING) AS v", "timestamp")
.withColumn("json", from_json(col("v"), click_schema))
.select("json.*", "timestamp")
.withColumn("event_ts", to_timestamp(col("ts")))
.withColumn("ingest_ts", current_timestamp())
.withColumn("dt", to_date(col("event_ts")))
.withWatermark("event_ts", "2 minutes")
.dropDuplicates(["event_id"]))


q_click = (click.writeStream
.format("parquet")
.outputMode("append")
.option("checkpointLocation", f"{checkpoint_root}/clickstream")
.option("path", f"{delta_root}/tables/clickstream")
.partitionBy("dt")
.trigger(processingTime="5 seconds")
.start())


# Simple aggregation: page views per minute per URL
click_agg = (click
.groupBy(window(col("event_ts"), "1 minute"), col("url"))
.agg(count("*").alias("pv"))
.select(col("window.start").alias("minute_start"), col("window.end").alias("minute_end"), "url", "pv")
.withColumn("dt", to_date(col("minute_start"))))


q_click_agg = (click_agg.writeStream
.format("parquet")
.outputMode("append")
.option("checkpointLocation", f"{checkpoint_root}/clickstream_agg")
.option("path", f"{delta_root}/tables/clickstream_agg")
.partitionBy("dt")
.trigger(processingTime="10 seconds")
.start())

# --------- IoT ---------
raw_iot = (spark.readStream
.format("kafka")
.option("kafka.bootstrap.servers", bootstrap)
.option("subscribe", iot_topic)
.option("startingOffsets", "earliest")
.load())


iot = (raw_iot
.selectExpr("CAST(key AS STRING) AS k", "CAST(value AS STRING) AS v", "timestamp")
.withColumn("json", from_json(col("v"), iot_schema))
.select("json.*", "timestamp")
.withColumn("event_ts", to_timestamp(col("ts")))
.withColumn("ingest_ts", current_timestamp())
.withColumn("dt", to_date(col("event_ts")))
.withWatermark("event_ts", "2 minutes")
.dropDuplicates(["device_id", "event_ts"]))


q_iot = (iot.writeStream
.format("parquet")
.outputMode("append")
.option("checkpointLocation", f"{checkpoint_root}/iot")
.option("path", f"{delta_root}/tables/iot")
.partitionBy("dt")
.trigger(processingTime="5 seconds")
.start())


# Keep both queries alive
spark.streams.awaitAnyTermination()