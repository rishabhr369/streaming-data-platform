#!/bin/bash
set -euo pipefail

echo "Waiting for Spark master to be ready..."
sleep 30

echo "Setting up Ivy environment..."
# Basic Ivy setup
export HOME=/tmp
export IVY_CACHE_DIR=/tmp/.ivy2
mkdir -p /tmp/.ivy2

echo "Submitting Spark streaming ETL job..."

/opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
    --repositories https://repo1.maven.org/maven2/ \
    --conf "spark.jars.ivy=/tmp/.ivy2" \
    --conf "spark.sql.streaming.forceDeleteTempCheckpointLocation=true" \
    --driver-memory 1g \
    --executor-memory 1g \
    --total-executor-cores 2 \
    /opt/jobs/streaming_etl.py

echo "Spark job completed."
