"""
 Counts words in UTF8 encoded, '\n' delimited text received from the network
 every second.
 Usage: spark_server.py <zk> <topic>
 To run this on your local machine, you need to setup Kafka and create
 a producer first, see http://kafka.apache.org/documentation.html#quickstart
 and then run the example
    `$ bin/spark-submit \
      --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 \
      spark/spark_server.py \
      localhost:2181 website-tracking website-report`
"""
from __future__ import print_function

import sys
import json

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v)
                                                        .encode('utf-8'))

def get_json(s):
    """
    Parse JSON from string.
    """
    try:
        return json.loads(s)
    except ValueError:
        return None


def handler(message, output_topic="website-report"):
    records = message.collect()
    print (records, "===============")
    for record in records:
        # TODO: Send output throught Kafka back to Node.js dashboard
        producer.send(output_topic, record[1])
        producer.flush()


def kafka_send(topic, message):
    print ("11111111111111111111111111111111111111111111")
    producer.send(topic, message)
    producer.flush()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: spark_server.py <zk> <input_topic> <output_topic>",
              file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="RealtimeDashboardTracking")
    sc.setLogLevel("WARN")

    ssc = StreamingContext(sc, 3)

    zkQuorum, topic, output_topic = sys.argv[1:]
    print ("zkQuorum", zkQuorum)
    print ("topic", topic)
    print ("output_topic", output_topic)

    kvs = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer",
                                  {topic: 1})

    # Format and filter DStream
    lines = kvs.map(lambda x: get_json(x[1]))
    lines.transform(lambda x: kafka_send(output_topic, {"hits": x}))

    # Send number of hits to output_topic
    lines.map(lambda rdd: kafka_send(output_topic, rdd))
    lines.pprint()

    ssc.start()
    ssc.awaitTermination()
