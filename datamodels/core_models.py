
from pydantic import BaseModel, Field

class LoginCredentials(BaseModel):
    email: str
    password: str

class RegisterUser(BaseModel):
    email: str = Field(min_length=5, max_length=50, pattern=".+@.+\..+")
    user_name: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=16)

class DomainSearchRequest(BaseModel):
    domain_url: str = Field(min_length=7)

class NewDomainRequest(BaseModel):
    base_url: str = Field(min_length=7)
    name: str = Field(min_length=3, max_length=25)




