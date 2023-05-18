from pydantic import BaseModel
from typing import Any
class Cameta_info(BaseModel):
    name: str
    url: str
    init_mode: str

class Member_info(BaseModel):
    name: str
    avatar: Any
    image: Any

class SUS_info(BaseModel):
    name: str
