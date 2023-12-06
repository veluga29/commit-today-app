from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, Literal


DT = TypeVar("DT")


class Response(BaseModel, Generic[DT]):
    ok: bool
    message: str
    data: DT


class ErrorResponse(BaseModel):
    ok: Literal[False]
    message: str
    data: None


class Cursors(BaseModel):
    prev: int | None = Field(None)
    next: int | None = Field(None)


class Paging(BaseModel):
    cursors: Cursors
    has_prev: bool
    has_next: bool


class PaginationResponse(Response):
    paging: Paging


class PaginationQueryParams(BaseModel):
    cursor: Optional[int] = Field(None)
    page_size: int = Field(10)
