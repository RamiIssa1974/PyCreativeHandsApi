from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

# ----- alias generators -----
def to_pascal(s: str) -> str:
    return "".join(w.capitalize() for w in s.split("_"))

def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(w.capitalize() for w in parts[1:])

class PascalModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_pascal)

class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

# ----- request -----
class GetUserRequest(CamelModel):
    user_name: Annotated[str, Field(validation_alias=AliasChoices("username","userName", "UserName"))]
    password: Annotated[str, Field(validation_alias=AliasChoices("password", "Password"))]

# ----- response -----
class UserOut(PascalModel):
    id: int
    user_name: str
    full_name: str | None = None
    is_admin: bool

class LoginResponse(PascalModel):
    token: str
    user: UserOut
