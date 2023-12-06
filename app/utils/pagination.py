from typing import TypeVar, Sequence

from app.domain.base_models import Base


T = TypeVar("T", bound=Base)


class CursorPagination:
    def __init__(self, cursor: int | None, page_size: int, curr_items: Sequence[T]):
        self.cursor = cursor
        self.page_size = page_size
        self.curr_items = curr_items
        self.prev_items = []
        self.next_items = []
        self.__prev_cursor = None
        self.__next_cursor = self.curr_items[-1].id if len(self.curr_items) == self.page_size else None
        self.__has_prev = False
        self.__has_next = False

    @property
    def next_cursor(self):
        return self.__next_cursor

    def _set_prev_cursor(self):
        if self.cursor:
            self.__prev_cursor = self.prev_items[-1].id if len(self.prev_items) == self.page_size else None
        else:
            self.__prev_cursor = None
    
    def _set_next_cursor(self):
        if self.__next_cursor and not self.next_items:
            self.__next_cursor = None

    def _set_has_prev(self):
        if self.cursor:
            self.__has_prev = True if self.prev_items else False
        else:
            self.__has_prev = False

    def _set_has_next(self):
        self.__has_next = bool(self.next_items) if self.__next_cursor else False

    def _get_paging(self, prev_items: Sequence[T], next_items: Sequence[T]):
        self.prev_items = prev_items
        self.next_items = next_items
        self._set_prev_cursor()
        self._set_next_cursor()
        self._set_has_prev()
        self._set_has_next()

        return dict(
            cursors=dict(prev=self.__prev_cursor, next=self.__next_cursor),
            has_prev=self.__has_prev,
            has_next=self.__has_next,
        )

    def get_pagiantion_response(self, prev_items: Sequence[T], next_items: Sequence[T]):
        return dict(
            data=[r.dict() for r in self.curr_items],
            paging=self._get_paging(prev_items=prev_items, next_items=next_items),
        )
