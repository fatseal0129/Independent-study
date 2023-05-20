from pydantic import BaseModel
from typing import Any
class CameraInfo(BaseModel):
    name: str
    mode: str
    url: str
    state: bool

class MemberInfo(BaseModel):
    name: str
    image: Any
    avatar: Any
