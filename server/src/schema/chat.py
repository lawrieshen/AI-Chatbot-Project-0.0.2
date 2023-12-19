from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid


class Message(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    msg: str
    timestamp: str = Field(default_factory=lambda: str(datetime.now()))


class Chat(BaseModel):
    token: str
    messages: List[Message]
    name: str
    session_start: str = Field(default_factory=lambda: str(datetime.now()))
