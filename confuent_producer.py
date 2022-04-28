from datetime import datetime
from bson.json_util import dumps, JSONOptions
from confluent_kafka import Producer
import time

def delivery_report(err, msg):
    if err:
        if str(type(err).__name__) == "KafkaError":
            print(f"Message failed with error : {str(err)}")
            print(f"Message Retry? :: {err.retriable()}")
        else:
            print(f"Message failed with error : {str(err)}")
    else:
        print(f"Message delivered to partition {msg.partition()}; Offset Value - {msg.offset()}")
        print(f"{msg.value()}")


def serializer(message):
    options = JSONOptions()
    options.datetime_representation = 2 # ISO-8601 datetime representation
    return dumps(message, json_options=options)
    #return json.dumps(message, default=str)


def kafka_producer(message):

    producer = Producer(
        {
            'bootstrap.servers': "116.202.190.91:9092"
        }
    )

    message_value = serializer(message)
    # message_key = {
    #     "format": "JSON",
    #     "content": "excess-mortality-prediction",
    #     "sender": "john.zaras@squaredev.io",
    #     "host": "squaredev.io",
    #     "program": "wsma-main.py",
    #     "timestamp": "2022-03-14T15:34:10Z",
    #     "trainingID": ""
    # }

    try:
        print()
        producer.poll(timeout=0)
        producer.produce(
            topic="STAMINA.ALL.EWS.EWS",
            # key=serializer(message_key),
            value=message_value,
            on_delivery=delivery_report
        )

    except BufferError as buffer_error:
        print(f"{buffer_error} :: Waiting until Queue gets some free space")
        time.sleep(1)

    producer.flush()