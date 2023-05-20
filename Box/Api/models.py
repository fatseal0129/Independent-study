from pydantic import BaseModel
from typing import Any
class Cameta_info(BaseModel):
    name: str
    url: str
    init_mode: str

