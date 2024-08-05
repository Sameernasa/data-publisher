from pydantic import BaseModel
from typing import Optional, List, Dict

class DestinationBase(BaseModel):
    url: str
    http_method: str
    headers: Dict[str, str]

class DestinationCreate(DestinationBase):
    pass

class Destination(DestinationBase):
    id: int
    account_id: int

    class Config:
        orm_mode = True

class DestinationResponse(BaseModel):
    id: int
    account_id: int
    url: str
    http_method: str

    class Config:
        orm_mode = True

class AccountBase(BaseModel):
    email: str
    account_name: str
    website: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    app_secret_token: str
    destinations: List[DestinationResponse] = []

    class Config:
        orm_mode = True
