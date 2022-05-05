from pydantic import BaseModel
from typing import Union, Any, Optional
from pydantic.utils import GetterDict


class SchemaTags(BaseModel):
    host: str
    region: str
    macAddress: str
    name: Optional[str]


class SchemaValue(BaseModel):
    unit: str
    value: float


class SchemaConfidence(BaseModel):
    unit: str
    value: float


class SchemaBloodOxFields(BaseModel):
    spo2: SchemaValue
    confidence: SchemaConfidence


class SchemaHrFields(BaseModel):
    hr: SchemaValue
    confidence: SchemaConfidence


class SchemaSkinTempFields(BaseModel):
    skinTemperature: SchemaValue


class SchemaStepsFields(BaseModel):
    stepCount: SchemaValue


class SchemaGeoFields(BaseModel):
    latitude: SchemaValue
    longitude: SchemaValue


class BasicSchema(BaseModel):
    measurement: str
    tags: SchemaTags
    time: int
    fields: Union[
        SchemaBloodOxFields,
        SchemaHrFields,
        SchemaSkinTempFields,
        SchemaStepsFields,
        SchemaGeoFields,
    ]
