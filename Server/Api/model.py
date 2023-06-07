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

class CameraStateInfo(BaseModel):
    name: str
    state: bool

class CameraModeInfo(BaseModel):
    name: str
    mode: str
