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


def emt_kafka_producer(message):

    producer = Producer(
        {
            'bootstrap.servers': "116.202.190.91:9092"
        }
    )
    basic_structure = {
        "server": "squaredev.io",
        "source": "EWS"
    }
    message_structure = basic_structure
    message_structure["entities"] = message
    message_value = serializer(message_structure)
    message_key = {
         "format": "JSON",
         "content": "emt_alerts",
         "sender": "innovation@squaredev.io",
         "host": "squaredev.io",
         "program": "ews.py",
         "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
         "trainingID": ""
     }
    
    try:
        producer.poll(timeout=0)
        producer.produce(
            topic="STAMINA.NL.ALL.EWS.COP",
            key=serializer(message_key),
            value=message_value,
            on_delivery=delivery_report
        )

    except BufferError as buffer_error:
        print(f"{buffer_error} :: Waiting until Queue gets some free space")
        time.sleep(1)

    producer.flush()