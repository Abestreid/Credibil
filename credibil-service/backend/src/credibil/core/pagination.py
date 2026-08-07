from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


@dataclass(frozen=True)
class PageParams:
    page: int = 1
    per_page: int = 25

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


class PaginationMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResult(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    items: Sequence[T]
    meta: PaginationMeta


def build_paginated_result(
    items: Sequence[T],
    total: int,
    page_params: PageParams,
) -> PaginatedResult[T]:
    total_pages = max(1, -(-total // page_params.per_page))
    return PaginatedResult(
        items=items,
        meta=PaginationMeta(
            page=page_params.page,
            per_page=page_params.per_page,
            total=total,
            total_pages=total_pages,
            has_next=page_params.page < total_pages,
            has_prev=page_params.page > 1,
        ),
    )


def parse_page_params(
    page: int | None = None,
    per_page: int | None = None,
    default: int = 25,
    max_size: int = 100,
) -> PageParams:
    p = page if page and page > 0 else 1
    pp = per_page if per_page and per_page > 0 else default
    pp = min(pp, max_size)
    return PageParams(page=p, per_page=pp)
