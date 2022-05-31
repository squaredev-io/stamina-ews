from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from actions import calculate_rules_on_smartko_data, find_geolocation_from_db, calculate_param_rules_on_smartko_data, calculate_combined_measurements
from utils import combine_docs_to_kafka
from confuent_producer import kafka_producer
from new_schema import BasicSchema as bs
from schemaBloodOxygen import SchemaProperties as schemaBO
from schemaHeartRate import SchemaProperties as schemaHR
from schemaSkinTemperature import SchemaProperties as schemaST
import os
from typing import List
from utils import *


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

params = load_params()
trial = params["trial"]

if trial== "General":
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
        # The list is returned from the API
        # Kafka will get one record at a time
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
                    "status": "no actions needed"
                }

                list_to_return.append(geo_data.copy())
                kafka_producer(geo_data)
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
                kafka_producer(health_data) 
                health_collection.insert_one(health_data)
        return list_to_return
elif trial=="AU":
    @app.post("/smartko_data")
    async def new_smartko_data(items: List[bs]):
        try:
            conn = MongoClient(connection_string)
            print("MongoDB connected successfully!!!")
        except:
            print("Could not connect to MongoDB")

        db = conn.ews
        health_collection = db.health
        geolocation_collection = db.geo
        # The list is returned from the API
        # Kafka will get one record at a time
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
                    "status": "no actions needed"
                }

                list_to_return.append(geo_data.copy())
                kafka_producer(geo_data)
                geolocation_collection.insert_one(geo_data)
            else:
                value = dict(fields[first_key])["value"]
                # TODO: needs work
                status, total_status = calculate_param_rules_on_smartko_data(measurement, value, trial, mac_address, time, db)
                latitude, longitude = find_geolocation_from_db(mac_address, db)
                # At first use the total status to send to kafka (is is based on past measurement)
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
                    "status": total_status
                }

                list_to_return.append(health_data.copy())
                kafka_producer([health_data]) 
                # After sending to kafka the total status based on past measurement
                # change it back to the status based on current measurement for storing in db
                health_data["status"] = status
                health_collection.insert_one(health_data)

                # Combination warnings/alerts
                if measurement == "heart_rate":
                    combined_status_oxy, first_doc, second_doc = calculate_combined_measurements(mac_address, db, True, True, time)
                    combine_docs_to_kafka(first_doc, second_doc, combined_status_oxy)
                    combined_status_temp, first_doc, second_doc = calculate_combined_measurements(mac_address, db, True, False, time)
                    combine_docs_to_kafka(first_doc, second_doc, combined_status_temp)

                elif measurement == "blood_oxygen":
                    combined_status_hr, first_doc, second_doc = calculate_combined_measurements(mac_address, db, True, True, time)
                    combine_docs_to_kafka(first_doc, second_doc, combined_status_hr)
                    combined_status_temp, first_doc, second_doc = calculate_combined_measurements(mac_address, db, False, True, time)
                    combine_docs_to_kafka(first_doc, second_doc, combined_status_temp)
                    
                elif measurement == "skin_temperature":
                    combined_status_hr, first_doc, second_doc = calculate_combined_measurements(mac_address, db, True, False, time)
                    combine_docs_to_kafka(first_doc, second_doc, combined_status_hr)
                    combined_status_oxy, first_doc, second_doc = calculate_combined_measurements(mac_address, db, False, True, time)
                    combine_docs_to_kafka(first_doc, second_doc, combined_status_oxy)
        
        return list_to_return

