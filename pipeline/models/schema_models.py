from pydantic import BaseModel, Field
from typing import List

class DBField(BaseModel):
    name: str
    type: str   # string | integer | boolean | datetime | text
    required: bool = True

class DBEntity(BaseModel):
    name: str
    fields: List[DBField]

class APIRoute(BaseModel):
    path: str
    method: str        # GET | POST | PUT | DELETE
    description: str
    roles: List[str] = []
    entity: str = ""   # which DB entity this maps to

class UIComponent(BaseModel):
    page: str
    components: List[str]
    accessible_by: List[str]
    api_routes: List[str] = []   # paths this page calls

class AuthRule(BaseModel):
    role: str
    permissions: List[str]   # read | write | delete | admin

class AppSchema(BaseModel):
    db_schema: List[DBEntity] = Field(default_factory=list)
    api_schema: List[APIRoute] = Field(default_factory=list)
    ui_schema: List[UIComponent] = Field(default_factory=list)
    auth_schema: List[AuthRule] = Field(default_factory=list)

class Permission(BaseModel):
    role: str
    access: List[str]

class DesignSchema(BaseModel):
    entities: List[str] = Field(default_factory=list)
    flows: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    permissions: List[Permission] = Field(default_factory=list)