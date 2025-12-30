"""
Authentication Utilities for FastAPI Application

This module contains utility functions and dependencies related to authentication and JWT (JSON Web Token) handling in a FastAPI application. It includes the following components:

1. Reusable OAuth2PasswordBearer:
   - This dependency provides a reusable OAuth2 authentication scheme to extract JWT tokens from the request header.
   - It expects the token to be provided in the "Authorization" header with the scheme name "JWT".

2. get_current_user Function:
   - This function is a dependency used to retrieve the currently authenticated user based on the JWT token.
   - It decodes the JWT token using the JWT_SECRET_KEY and validates it using the specified ALGORITHM.
   - If the token is expired or invalid, appropriate HTTPExceptions are raised.
   - If the token is valid, it extracts the user's payload (TokenPayload) from the decoded token.
   - The user's ID (sub attribute in the token payload) is used to fetch user data from the Replit db (a simple key-value store).
   - If the user is found, a SystemUser model instance is returned.
   - If the user is not found, an HTTPException with status code 404 (Not Found) is raised.

Developer: Ashish Kumar

Website: https://ashishkrb7.github.io/

Contact Email: ashish.krb7@gmail.com
"""

from datetime import datetime
from typing import Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from schemas import SystemUser, TokenPayload
from utils import ALGORITHM, JWT_SECRET_KEY

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")


async def get_current_user(token: str = Depends(reuseable_oauth)) -> SystemUser:
    """
    Dependency to get the currently authenticated user.

    Args:
        token (str): JWT token extracted from the "Authorization" header.

    Returns:
        SystemUser: An instance of SystemUser representing the currently authenticated user.

    Raises:
        HTTPException: If the token is expired, invalid, or if the user is not found.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: Union[dict[str, Any], None] = db.get(token_data.sub, None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return SystemUser(**user)
