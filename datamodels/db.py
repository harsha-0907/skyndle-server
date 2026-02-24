
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    user_name = Column(String(20))
    email = Column(String(50), unique=True)
    created_at = Column(TIMESTAMP)

class Credentials(Base):
    __tablename__ = "credentials"

    email = Column(String(50), ForeignKey("users.email", ondelete="CASCADE"), primary_key=True)
    password = Column(String(16), nullable=False)
    reset_key = Column(String(16), unique=True, nullable=False)
    valid_upto = Column(TIMESTAMP)

class Domains(Base):
    __tablename__ = "domains"

    domain_id = Column(Integer, autoincrement=True, primary_key=True)
    domain_name = Column(String(25), nullable=False)
    domain_base_url = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP)
    last_updated_at = Column(TIMESTAMP)

class URLs(Base):
    __tablename__ = "urls"

    url_id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(100), nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.domain_id", ondelete="CASCADE"))

