from pydantic import BaseModel, Field


class SchemaHeartRateProperties(BaseModel):
    unit: str
    value: int


class SchemaHeartRate(BaseModel):
    properties: SchemaHeartRateProperties = Field(...)


class SchemaFieldsProperties(BaseModel):
    heart_rate: SchemaHeartRate = Field(...)


class SchemaFields(BaseModel):
    properties: SchemaFieldsProperties


class SchemaProperties(BaseModel):
    measurement: str = Field(...)
    time: str = Field(...)
    fields: SchemaFields = Field(...)
