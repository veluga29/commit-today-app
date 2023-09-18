from dataclasses import dataclass
from app.domain.base_models import Base


@dataclass
class User(Base):
    fullname: str
    username: str
    email: str
    password: str
