from fastapi import FastAPI
from pymongo import MongoClient
from actions import check_BO_data, check_HR_data, check_ST_data
from schemaBloodOxygen import SchemaProperties as schemaBO
from schemaHeartRate import SchemaProperties as schemaHR
from schemaSkinTemperature import SchemaProperties as schemaST
import os


app = FastAPI()
connection_string = os.getenv("CONNECTION_STRING", "mongodb://localhost:27017/stamina_ews")
print(connection_string)

@app.post("/blood_oxygen")
async def blood_oxygen(item: schemaBO):
    try:
        conn = MongoClient(connection_string)
        print("MongoDB connected successfully!!!")
    except:
        print("Could not connect to MongoDB")

    db = conn.ews
    collection = db.healthData_collection

    measurement = item.measurement
    time = item.time
    blood_oxygen_properties = item.fields.properties.blood_oxygen.properties
    blood_oxygen_value = blood_oxygen_properties.value
    blood_oxygen_unit = blood_oxygen_properties.unit
    bo_status = check_BO_data(blood_oxygen_value)

    healthData = [{"Measurement": measurement, "Time": time,
                   "Blood_oxygen_value": blood_oxygen_value, "Blood_oxygen_unit": blood_oxygen_unit,
                   "Blood_oxygen_status": bo_status}]

    for data in healthData:
        collection.insert_one(data)


@app.post("/heart_rate")
async def heart_rate(item: schemaHR):
    try:
        conn = MongoClient("mongodb://localhost:27017/")
        print("MongoDB connected successfully!!!")
    except:
        print("Could not connect to MongoDB")

    db = conn.ews
    collection = db.healthData_collection

    measurement = item.measurement
    time = item.time
    heart_rate_properties = item.fields.properties.heart_rate.properties
    heart_rate_value = heart_rate_properties.value
    heart_rate_unit = heart_rate_properties.unit
    hr_status = check_HR_data(heart_rate_value)

    healthData = [{"Measurement": measurement, "Time": time,
                   "Heart_rate_value": heart_rate_value, "Heart_rate_unit": heart_rate_unit,
                   "Heart_rate_status": hr_status}]

    for data in healthData:
        collection.insert_one(data)


@app.post("/skin_temp")
async def skin_temp(item: schemaST):
    try:
        conn = MongoClient("mongodb://localhost:27017/")
        print("MongoDB connected successfully!!!")
    except:
        print("Could not connect to MongoDB")

    db = conn.ews
    collection = db.healthData_collection

    measurement = item.measurement
    time = item.time
    skin_temperature_properties = item.fields.properties.skin_temp.properties
    skin_temperature_value = skin_temperature_properties.value
    skin_temperature_unit = skin_temperature_properties.unit
    st_status = check_ST_data(skin_temperature_value)
    healthData = [{"Measurement": measurement, "Time": time,
                   "Skin_temperature_value": skin_temperature_value, "Skin_temperature_unit": skin_temperature_unit,
                   "Skin_temperature_status": st_status}]

    for data in healthData:
        collection.insert_one(data)
