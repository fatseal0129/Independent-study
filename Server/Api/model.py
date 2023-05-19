from pydantic import BaseModel
class CameraInfo(BaseModel):
    name: str
    mode: str
    state: bool
