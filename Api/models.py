from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum, unique


# unique 能夠檢查列舉是否有重複的列舉值
@unique
class Gender(str, Enum):
    male = "male"
    female = "female"
    unwilling = "unwilling"


class Role(str, Enum):
    admin = "admin"
    user = "user"
    student = "student"


class User(BaseModel):
    id: Optional[UUID] = uuid4()
    name: str
    gender: Gender
    path: List[str]

class UserUpdateRequest(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]
    roles: Optional[List[Role]]

