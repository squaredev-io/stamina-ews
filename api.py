from fastapi import FastAPI
from pydantic import BaseModel, Field
from mongo import db
from pymongo import MongoClient


class SchemaBloodOxProperties(BaseModel):
    unit: str
    value: int


class SchemaBloodOx(BaseModel):
    properties: SchemaBloodOxProperties = Field(...)


class SchemaFieldsProperties(BaseModel):
    blood_oxygen: SchemaBloodOx = Field(...)


class SchemaFields(BaseModel):
    properties: SchemaFieldsProperties


class SchemaProperties(BaseModel):
    measurement: str = Field(...)
    time: str = Field(...)
    fields: SchemaFields = Field(...)


app = FastAPI()


def check_ST_data(st):
    # st stands for skin_temperature
    if st > 37 and st < 37.5:
        status = "Warning"
        return status
    elif st < 28 or st >= 37.5:
        status = "Alert"
        return status
    else:
        status = "No actions needed"
        return status


def check_HR_data(hr):
    # hr stands for heart_rate
    if hr > 100 and hr < 105:
        status = "Warning"
        return status
    elif hr >= 105 or hr < 60:
        status = "Alert"
        return status
    else:
        status = "No actions needed"
        return status


def check_BO_data(bo):
    # bo stands for blood_oxygen
    if bo <= 90 and bo >= 85:
        status = "Warning"
        return status
    elif bo < 85:
        status = "Alert"
        return status
    else:
        status = "No actions needed"
        return status


@app.post("/")
async def data_posted(item: SchemaProperties):
    try:
        conn = MongoClient("mongodb://localhost:27017/")
        print("MongoDB connected successfully!!!")
    except:
        print("Could not connect to MongoDB")

    db = conn.database
    collection = db.healthData_collection

    measurement = item.measurement
    time = item.time
    blood_oxygenProperties = item.fields.properties.blood_oxygen.properties
    blood_oxygenValue = blood_oxygenProperties.value
    blood_oxygenUnit = blood_oxygenProperties.unit

    status = check_BO_data(blood_oxygenValue)

    healthData = [{"Measurement": measurement, "Time": time,
                   "Blood_oxygenValue": blood_oxygenValue, "Blood_oxygenUnit": blood_oxygenUnit, "Status": status}]

    for data in healthData:
        collection.insert_one(data)
