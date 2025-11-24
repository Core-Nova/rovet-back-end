"""
Request validation dependencies.

Provides reusable validation logic for common request parameters.
"""

from fastapi import HTTPException, status


def validate_pagination(
    page: int = 1,
    size: int = 10
) -> tuple[int, int]:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        size: Page size
        
    Returns:
        tuple: Validated (page, size)
        
    Raises:
        HTTPException: 400 if parameters are invalid
        
    Example:
        ```python
        @router.get("/items")
        def get_items(pagination: tuple = Depends(validate_pagination)):
            page, size = pagination
            ...
        ```
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1"
        )
    if size < 1 or size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Size must be between 1 and 100"
        )
    return page, size

