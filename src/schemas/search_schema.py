from typing import Any, Dict, List, Union
from pydantic import BaseModel

class MatchAnyOrInterval(BaseModel):
    any: List[str] = None
    gt: str = None #greater than
    gte: str = None #greater than or equals to
    lt: str = None #less than
    lte: str = None

    class Config:
        arbitrary_types_allowed = True