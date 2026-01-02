"""
FastAPI Authentication Endpoints

This script contains the FastAPI endpoints responsible for user authentication and user-related actions. It includes the following endpoints:

1. /signup:
   - Method: POST
   - Summary: Create a new user.
   - Description: This endpoint allows users to sign up by providing their email and password. It checks if the user already exists in the database and raises an HTTPException if the user already has an account. If the user is new, their data is hashed, and a unique identifier (UUID) is generated for the user. The user's data is then saved to the database.
   - Response Model: UserOut (User output model containing user's email and unique identifier).

2. /login:
   - Method: POST
   - Summary: Create access and refresh tokens for the user.
   - Description: This endpoint allows users to log in using their email and password. It verifies the user's credentials by checking the hashed password against the one stored in the database. If the credentials are valid, the endpoint generates and returns both an access token and a refresh token for the user. These tokens can be used for authentication in subsequent requests.
   - Response Model: TokenSchema (Schema for JWT tokens containing access_token and refresh_token attributes).

3. /me:
   - Method: GET
   - Summary: Get details of the currently logged-in user.
   - Description: This endpoint requires a valid JWT access token to be provided in the Authorization header. It uses the get_current_user dependency (SystemUser) to extract and validate the user's information from the token payload. If the token is valid and the user is found in the database, their details are returned in the response.
   - Response Model: UserOut (User output model containing user's email and unique identifier).

4. /reset_email:
   - Method: POST
   - Summary: Reset user's email address.
   - Description: This endpoint allows users to reset their email address and update their password. It requires the user's current email address, new email address, current password, and new password. It verifies the provided credentials and updates the user's data in the database.
   - Response Model: UserOut (User output model containing updated email and unique identifier).

Developer: Ashish Kumar

Website: https://ashishkrb7.github.io/

Contact Email: ashish.krb7@gmail.com
"""

import os
from uuid import uuid4

from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

import database
from deps import get_current_user
from schemas import SystemUser, TokenSchema, UserAuth, UserOut
from utils import (
    create_access_token,
    create_refresh_token,
    get_hashed_password,
    verify_password,
)

if not os.path.exists(database.DATABASE_FILE):
    # Create the table in the database
    database.create_table()

app = FastAPI()


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def docs():
    """
    Redirect to the API documentation (Swagger UI).
    """
    return RedirectResponse(url="/docs")


@app.post("/signup", summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):
    """
    Endpoint to create a new user.

    Args:
        data (UserAuth): User authentication model containing user's email and password.

    Returns:
        dict: The user data containing email and unique identifier (UUID).

    Raises:
        HTTPException: If a user with the same email already exists in the database (status code 400).
    """
    # Query the database to check if the user already exists
    user = database.get_data(data.email)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Insert the new user data into the database
    user = {
        "email": data.email,
        "password": get_hashed_password(data.password),
        "id": str(uuid4()),
    }
    database.insert_data(data.email, user)

    return user


@app.post(
    "/login",
    summary="Create access and refresh tokens for user",
    response_model=TokenSchema,
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to create access and refresh tokens for a user upon successful login.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): OAuth2 password request form containing username and password.

    Returns:
        dict: Dictionary containing access_token and refresh_token as keys.

    Raises:
        HTTPException: If the provided email or password is incorrect (status code 400).
    """
    # Retrieve user data from the database based on the email
    user = database.get_data(form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    # Verify the provided password against the hashed password in the database
    hashed_pass = user["password"]
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    # Create and return the access and refresh tokens
    return {
        "access_token": create_access_token(user["email"]),
        "refresh_token": create_refresh_token(user["email"]),
    }


@app.get(
    "/me", summary="Get details of currently logged in user", response_model=UserOut
)
async def get_me(user: SystemUser = Depends(get_current_user)):
    """
    Endpoint to get details of the currently logged-in user. You will be able to see the Authorize button in the swagger docs and a 🔒 icon in front of the protected endpoint /me

    Args:
        user (SystemUser, optional): SystemUser instance representing the currently authenticated user.

    Returns:
        dict: User data containing email and unique identifier (UUID).

    Raises:
        HTTPException: If the user is not found in the database (status code 404).
    """
    return user


@app.post(
    "/reset_email",
    summary="Reset user's email address",
    response_model=UserOut,
)
async def reset_email(
    email: EmailStr = Form(...),
    new_email: EmailStr = Form(...),
    password: str = Form(...),
    new_password: str = Form(...),
):
    """
    Endpoint to reset the user's email address.

    Args:
        email (str): User's current email address.
        new_email (str): New email address to set.
        password (str): User's current password for authentication.
        new_password (str): New password to set.

    Returns:
        dict: The updated user data containing new email and unique identifier (UUID).

    Raises:
        HTTPException: If the provided email or password is incorrect (status code 400).
    """
    # Retrieve user data from the database based on the email
    user = database.get_data(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    # Verify the provided password against the hashed password in the database
    hashed_pass = user["password"]
    if not verify_password(password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    # Delete the old row with the previous email address
    database.delete_data(email)

    # Update the user's email and password in the database
    user["email"] = new_email
    user["password"] = get_hashed_password(new_password)
    database.insert_data(new_email, user)

    return user
