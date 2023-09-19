from abc import ABCMeta
from dataclasses import dataclass
from datetime import datetime


@dataclass(eq=False)
class Base(metaclass=ABCMeta):
    id: int
    created_at: datetime
    updated_at: datetime
