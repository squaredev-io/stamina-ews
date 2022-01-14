from datetime import datetime
from kafka import KafkaConsumer
from mongo import db
from json import loads


def start():
    consumer = KafkaConsumer(
        "RE",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest",
        enable_auto_commit=True,
        auto_commit_interval_ms=1000,
        group_id="rule-engine",
        value_deserializer=lambda x: loads(x.decode("utf-8")),
    )

    print("start consumer: connected")
    for message in consumer:
        message = message.value

        db[message["type"]].insert_one(message)
        print(f"{message} added to {message['type']}")


start()
