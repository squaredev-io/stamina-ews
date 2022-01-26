from pydantic import BaseModel, Field


class SchemaBloodOxProperties(BaseModel):
    unit: str
    value: float


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
