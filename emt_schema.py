from pydantic import BaseModel
from typing import List, Union

class EmtReportEntitySchema(BaseModel):
    id: str
    type: str
    value: Union[int, float]
    location: List[str] = None
    warning: bool
    alert: bool
