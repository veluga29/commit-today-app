from abc import ABCMeta
from dataclasses import dataclass
from datetime import datetime
from dataclasses import field


@dataclass(eq=False)
class Base(metaclass=ABCMeta):
    id: int = field(init=False)
    created_at: datetime = field(init=False)
    updated_at: datetime = field(init=False)
