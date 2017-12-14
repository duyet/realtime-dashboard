
source "$(dirname "$0")"/env.sh

$SPARK_HOME/bin/spark-submit \
	--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 \
	$RRD_HOME/spark/spark_server.py \
	localhost:2181 website-collect website-report
