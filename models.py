from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
import uuid
import json

from database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    account_name = Column(String, nullable=False)
    app_secret_token = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    website = Column(String)

    destinations = relationship("Destination", back_populates="account", cascade="all, delete-orphan")

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    http_method = Column(String, nullable=False)
    headers = Column(String, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"))

    account = relationship("Account", back_populates="destinations")

    def __init__(self, url, http_method, headers, account_id):

        self.url = url
        self.http_method = http_method
        self.headers = json.dumps(headers)  
        self.account_id = account_id

    @property
    def headers_dict(self):
        return json.loads(self.headers)  

    @headers_dict.setter
    def headers_dict(self, value):
        
        self.headers = json.dumps(value) 
