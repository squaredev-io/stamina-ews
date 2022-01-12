from consts import EventType
from time import sleep
from json import dumps
from kafka import KafkaProducer
from datetime import datetime, timedelta
from bson import json_util

"""
This producer is created for testing purposes. Also it can be used as a replacement of PPT.
"""

producer = KafkaProducer(
    bootstrap_servers=["127.0.0.1:9092"],
    security_protocol="SSL",
    value_serializer=lambda x: dumps(
        x, default=json_util.default).encode("utf-8"),
)

"""
Send data for the PCR case.
"""
for e in range(10):
    data = dict(
        type=EventType.pcr,
        positive_percentage=4,
        country="GR",
        region="Chania",
        date_created=(datetime.now() - timedelta(days=e)).strftime("%Y-%m-%d"),
    )

    producer.send("RE", value=data)
    print("Sent type: ", data["type"], e)

    sleep(2)


"""
Send data for the beds case.
"""
for e in range(10):
    data = dict(
        type=EventType.icu_beds_completeness,
        completeness_percentage=50,
        country="GR",
        region="Chania",
        date_created=(datetime.now() - timedelta(days=e)).strftime("%Y-%m-%d"),
    )

    producer.send("RE", value=data)
    print("Sent type: ", data["type"], e)

    sleep(2)


print("done")
