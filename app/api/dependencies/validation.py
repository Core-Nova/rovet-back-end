from fastapi import HTTPException, status


def validate_pagination(page: int, size: int) -> None:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number (must be >= 1)
        size: Page size (must be between 1 and 100)
    
    Raises:
        HTTPException: If validation fails
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1"
        )
    elif size < 1 or size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Size must be between 1 and 100"
        )

