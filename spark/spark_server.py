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
from kafka import SimpleProducer, KafkaClient
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


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: spark_server.py <zk> <input_topic> <output_topic>",
              file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="RealtimeDashboardTracking")
    sc.setLogLevel("WARN")

    ssc = StreamingContext(sc, 3)

    zkQuorum, topic, output_topic = sys.argv[1:]
    kvs = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer",
                                  {topic: 1})

    kvs.count().map(lambda x: 'Number of event this batch: %s' % x).pprint()
    lines = kvs.map(lambda x: get_json(x[1])).filter(lambda x: x)
    lines.pprint()

    kvs.foreachRDD(lambda message: handler(message, output_topic))

    ssc.start()
    ssc.awaitTermination()
