#!/usr/bin/env bash
set -euo pipefail


BS="kafka-1:9092"
PARTS="${KAFKA_PARTITIONS:-6}"
RF="${KAFKA_REPLICATION_FACTOR:-3}"
MINISR="${KAFKA_MIN_INSYNC:-2}"


echo "Waiting for Kafka at $BS ..."
for i in {1..60}; do
if /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server "$BS" --list >/dev/null 2>&1; then
break
fi
sleep 2
if [[ $i -eq 60 ]]; then echo "Kafka not ready"; exit 1; fi
done


create_topic() {
local t="$1"
/opt/bitnami/kafka/bin/kafka-topics.sh \
--bootstrap-server "$BS" \
--create \
--topic "$t" \
--partitions "$PARTS" \
--replication-factor "$RF" \
--config min.insync.replicas="$MINISR" \
|| true
}


create_topic clickstream
create_topic iot


/opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server "$BS" --describe --topic clickstream || true
/opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server "$BS" --describe --topic iot || true


echo "Topics created."