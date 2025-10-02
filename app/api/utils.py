"""
Helper utilities for API responses and pagination.
"""

import math
from typing import TypeVar

from app.schemas.response import PaginatedResponse, PaginationMeta

T = TypeVar("T")


def create_pagination_meta(
    page: int,
    per_page: int,
    total: int,
) -> PaginationMeta:
    """
    Create pagination metadata.

    Args:
        page: Current page number (1-indexed)
        per_page: Number of items per page
        total: Total number of items

    Returns:
        PaginationMeta object with calculated values
    """
    total_pages = math.ceil(total / per_page) if per_page > 0 else 0

    return PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


def create_paginated_response[T](
    data: list[T],
    page: int,
    per_page: int,
    total: int,
    message: str = "Resources retrieved successfully",
) -> PaginatedResponse[T]:
    """
    Create a paginated response with data and metadata.

    Args:
        data: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        message: Success message

    Returns:
        Dictionary ready to be returned from endpoint
    """
    pagination = create_pagination_meta(page, per_page, total)
    return PaginatedResponse[T](
        success=True,
        message=message,
        data=data,
        pagination=pagination,
    )


def get_skip_limit(page: int = 1, per_page: int = 20) -> tuple[int, int]:
    """
    Calculate skip and limit values for database queries.

    Args:
        page: Current page number (1-indexed)
        per_page: Number of items per page

    Returns:
        Tuple of (skip, limit) for use in database queries
    """
    skip = (page - 1) * per_page
    limit = per_page
    return skip, limit
