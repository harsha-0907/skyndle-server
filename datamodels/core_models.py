
from enum import Enum
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

# Enum
class ScanType(str, Enum):
    INVASIVE = "INVASIVE"
    REGULAR = "REGULAR"

class ScanProfile(str, Enum):
    AUTHENTICATED = "AUTHENTICATED"
    REGULAR = "REGULAR"

class DomainSize(Enum):
    MICRO = "MICRO"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    VERYLARGE = "VERYLARGE"
    EXTREME = "EXTREME"

class Phase(Enum):
    INIT = "INIT"
    DISCOVERY = "DISCOVERY"
    CRAWLING = "CRAWLING"
    CONCLUSION = "CONCLUSION"

class NewDomainRequest(BaseModel):
    base_url: str = Field(min_length=7)
    name: str = Field(min_length=3, max_length=25)
    scan_type: ScanType = Field(default=ScanType.REGULAR)
    scan_profile: ScanProfile = Field(default=ScanProfile.REGULAR)
    auth_header: str = Field(max_length=150)    # This is the field that accepts the authentication header






