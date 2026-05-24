from pydantic import BaseModel
from typing import List


class Field(BaseModel):
    name : str
    type : str
    required : bool = True

class Entity(BaseModel):
    name : str
    fields : List[Field]

class Relationship(BaseModel):
    source : str
    target : str
    relation_type : str

class APIRoute (BaseModel):
    path : str
    method: str 
    description : str

class System_schema (BaseModel):
    entities : List[Entity]
    relationships : List[Relationship]
    api_routes : List[APIRoute]


