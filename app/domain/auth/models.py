from dataclasses import dataclass, field
from app.domain.base_models import Base


@dataclass
class User(Base):
    email: str = field(default="")
    password: str = field(default="")
    username: str = field(default="")
    last_name: str = field(default="")
    first_name: str = field(default="")

