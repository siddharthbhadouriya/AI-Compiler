from pydantic import BaseModel, Field
from typing import List

class Permission(BaseModel):
    role : str
    access : List[str]

class DesignSchema(BaseModel):
    entities : List[str] = Field(default_factory=list)
    flows : List[str]  = Field(default_factory=list)
    roles : List[str] = Field(default_factory=list)
    permissions : List[Permission] = Field(default_factory=list)

