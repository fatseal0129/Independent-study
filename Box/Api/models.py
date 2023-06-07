from pydantic import BaseModel
from typing import Any
class Camera_info(BaseModel):
    name: str
    url: str
    init_mode: str

class Camera_change_mode(BaseModel):
    name: str
    mode: str

