<style>.markdown-preview {background: #FFF !important; color: #1f1f1f !important} .markdown-preview h1, .markdown-preview h2, .markdown-preview h3, .markdown-preview h4, .markdown-preview h5, .markdown-preview p {background: #FFF !important; color: #1f1f1f !important}</style>

# Realtime Dashboard
Real-time report dashboard with Apache Kafka, Apache Spark Streaming and Node.js

![](RRD.png)

# Getting started

## 1. Setup environment

Clone this project

```sh
git clone https://github.com/duyetdev/realtime-dashboard.git
cd realtime-dashboard/

# Setup env
./bin/env.sh
```

Download [Apache Spark 2.2.0](http://spark.apache.org/downloads.html)

```sh
cd $REALTIME_DASHBOARD_HOME
wget https://www.apache.org/dyn/closer.lua/spark/spark-2.2.0/spark-2.2.0-bin-hadoop2.7.tgz
tar -xzf spark-2.2.0-bin-hadoop2.7.tgz
export SPARK_HOME=$REALTIME_DASHBOARD_HOME/spark-2.2.0-bin-hadoop2.7
```

Download Kafka
```sh
cd $REALTIME_DASHBOARD_HOME
wget http://mirrors.viethosting.com/apache/kafka/1.0.0/kafka_2.11-1.0.0.tgz
tar -xzf kafka_2.11-1.0.0.tgz
export KAFKA_HOME=$REALTIME_DASHBOARD_HOME/kafka_2.11-1.0.0
```

Download Kafka Proxy
```sh
cd $REALTIME_DASHBOARD_HOME
curl -L https://github.com/mailgun/kafka-pixy/releases/download/v0.14.0/kafka-pixy-v0.14.0-linux-amd64.tar.gz | tar xz
cd kafka-pixy-v0.14.0-linux-amd64
cp default.yaml config.yaml
```


## 2. Start Kafka Server

Start Zookeeper and Kafka
```sh
cd $REALTIME_DASHBOARD_HOME/kafka_2.11-1.0.0

# Start zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties &

# Start Kafka
bin/kafka-server-start.sh config/server.properties &
```

Create Topics
```sh
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic website-collect
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic website-report
```

We can't access Kafka directly via HTTP, so we start **Kafka Proxy** :
```sh
cd $REALTIME_DASHBOARD_HOME/kafka-pixy-v0.14.0-linux-amd64
./kafka-pixy --config config.yaml
```

Test (Optional) Kafka Produder and Consumer

Open two terminals:
```sh
# Terminal 1
$ bin/kafka-console-producer.sh --broker-list localhost:9092 --topic website-collect
This is a message
This is another message
{"client_id": "blog.duyet.net", "time": "1510736940", "event": "view", "ip":"1.2.3.4", "UA": "Chrome"}
{"client_id": "blog.duyet.net", "time": "1510736940", "event": "click", "ip":"1.2.3.5", "UA": "Firefox"}
```

```sh
# Terminal 2
$ bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic website-collect --from-beginning
This is a message
This is another message
{"client_id": "blog.duyet.net", "time": "1510736940", "event": "view", "ip":"1.2.3.4", "UA": "Chrome"}
{"client_id": "blog.duyet.net", "time": "1510736940", "event": "click", "ip":"1.2.3.5", "UA": "Firefox"}
```

## 3. Apache Spark Streaming

![](https://spark.apache.org/docs/latest/img/streaming-arch.png)

Submit Spark Streaming script

```sh
# Usage: spark_server.py <zk> <input_topic> <output_topic>

$SPARK_HOME/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 \
    $REALTIME_DASHBOARD_HOME/spark/spark_server.py \
    localhost:2181 website-tracking website-report
```
