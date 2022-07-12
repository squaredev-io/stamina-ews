from datetime import datetime
from bson.json_util import loads, dumps, JSONOptions
from confluent_kafka import Consumer
import time


def consumer():

    kafka_topic = "TOPIC_TO_LISTEN"

    consumer = Consumer(
        {
            "bootstrap.servers": "116.202.190.91:9092",
            "group.id": "squaedev",
            "auto.offset.reset": "earliest",
        }
    )

    # Subscribe to topic
    consumer.subscribe([kafka_topic])

    message_list = []
    counter = 0
    n_messages = 0

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print(f"Waiting for another {10 - counter} seconds")
                counter += 1
                if counter == 10:
                    break
            elif message.error():
                print("ERROR: %s".format(message.error()))
            else:
                # Extract the (optional) key and value, and print.
                deserialized_msg = loads(message.value())
                for datum in deserialized_msg["context"]["data"]["data"]:
                    n_messages += 1
                    print(f"Consumed {n_messages} messages")
                    message_list.append(datum)
                counter = 0
        if n_messages == 0:
            print("No messages consumed")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
        print("Kafka connection closed")

    return message_list
