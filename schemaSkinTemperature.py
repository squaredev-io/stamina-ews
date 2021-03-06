from pydantic import BaseModel, Field


class SchemaSkinTempProperties(BaseModel):
    unit: str
    value: float


class SchemaSkinTemperature(BaseModel):
    properties: SchemaSkinTempProperties = Field(...)


class SchemaFieldsProperties(BaseModel):
    skin_temp: SchemaSkinTemperature = Field(...)


class SchemaFields(BaseModel):
    properties: SchemaFieldsProperties


class SchemaProperties(BaseModel):
    measurement: str = Field(...)
    time: str = Field(...)
    fields: SchemaFields = Field(...)
