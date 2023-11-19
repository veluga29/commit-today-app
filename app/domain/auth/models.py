import bcrypt
from dataclasses import dataclass, field

from app import settings
from app.domain.base_models import Base


@dataclass
class User(Base):
    email: str = field(default="")
    password: str = field(default="")
    username: str = field(default="")
    last_name: str = field(default="")
    first_name: str = field(default="")

    def dict(self) -> dict:
        return dict(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            email=self.email,
            password=self.password,
            username=self.username,
            last_name=self.last_name,
            first_name=self.first_name,
        )
    
    def hash_password(self) -> None:
        hashed_password: bytes = bcrypt.hashpw(
            self.password.encode(settings.AUTH_SETTINGS.HASH_ENCODING),
            salt=bcrypt.gensalt(),
        )
        self.password = hashed_password.decode(settings.AUTH_SETTINGS.HASH_ENCODING)
    
    def verify_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(settings.AUTH_SETTINGS.HASH_ENCODING),
            self.password.encode(settings.AUTH_SETTINGS.HASH_ENCODING)
        )
