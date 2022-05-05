from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from actions import calculate_rules_on_smartko_data, find_geolocation_from_db
from confuent_producer import kafka_producer
from new_schema import BasicSchema as bs
from schemaBloodOxygen import SchemaProperties as schemaBO
from schemaHeartRate import SchemaProperties as schemaHR
from schemaSkinTemperature import SchemaProperties as schemaST
import os
from typing import List


app = FastAPI()
origins = [
"*"
]

app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

connection_string = os.getenv(
    "CONNECTION_STRING", "mongodb://localhost:27017/stamina_ews"
)
print(connection_string)


@app.post("/smartko_data")
async def smartko_data(items: List[bs]):
    try:
        conn = MongoClient(connection_string)
        print("MongoDB connected successfully!!!")
    except:
        print("Could not connect to MongoDB")

    db = conn.ews
    health_collection = db.health
    geolocation_collection = db.geo

    list_to_return = []
    for item in items:
        measurement = item.measurement
        time = item.time
        tags = dict(item.tags)
        host = tags["host"]
        region = tags["region"]
        mac_address = tags["macAddress"]

        if "name" in tags:
            name = tags["name"]
        else:
            name = None
        
        fields = dict(item.fields)
        keys_in_fields = list(fields.keys())
        first_key = keys_in_fields[0]
        unit = dict(fields[first_key])["unit"]

        if measurement == "geo_location":
            second_key = keys_in_fields[1]
            latitude = dict(fields[first_key])["value"]
            longitude = dict(fields[second_key])["value"]

            geo_data = {
                "measurement": measurement,
                "host": host,
                "time": time,
                "region": region,
                "latitude": latitude,
                "longitude": longitude,
                "unit": unit,
                "mac_address": mac_address,
            }

            list_to_return.append(geo_data.copy())
            geolocation_collection.insert_one(geo_data)

        else:
            value = dict(fields[first_key])["value"]
            status = calculate_rules_on_smartko_data(measurement, value)
            latitude, longitude = find_geolocation_from_db(mac_address, db)

            health_data = {
                "measurement": measurement,
                "host": host,
                "time": time,
                "value": value,
                "unit": unit,
                "region": region,
                "latitude": latitude,
                "longitude": longitude,
                "mac_address": mac_address,
                "name": name,
                "status": status
            }

            list_to_return.append(health_data.copy())
            health_collection.insert_one(health_data)

    kafka_producer(list_to_return)

    return list_to_return
