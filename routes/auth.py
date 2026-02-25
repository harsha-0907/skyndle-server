
import aiofiles
from datetime import datetime
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from datamodels.db import get_db_session, Credentials, Users
from utils.jwt_utils import encode_jwt, decode_jwt
from datamodels.core_models import LoginCredentials, RegisterUser
from fastapi import APIRouter, Request, Body, Depends
from utils.helper_functions import generate_id

router = APIRouter()

@router.get("/login")
async def get_login_page():
    """ Returns the HTML Login Page """

    html_content = None
    async with aiofiles.open("src/html/login.html", 'r') as file:
        html_content = await file.read()

    return HTMLResponse(content=html_content, status_code=200)

@router.post("/login")
def login_user(session=Depends(get_db_session), credentials: LoginCredentials = Body(...)):
    """ Endpoint to fetch Auth token """

    req_email = credentials.email
    req_password = credentials.password

    user_credential = session.query(Credentials).filter(Credentials.email == req_email).first()
    print(user_credential.__dict__)

    if user_credential is None or user_credential.password != req_password:
        # Return a 401 response
        return JSONResponse(content={"message": "Invalid Credentials"}, status_code=401)
    
    # Valid Credentials
    reset_jwt_key = encode_jwt({"reset_key": generate_id()}, expires_in=86400*7)

    payload = {
        "session_id": generate_id(),
        "user_email": user_credential.email,
        "reset_key": reset_jwt_key
    }
    auth_jwt_token = encode_jwt(payload, expires_in=3600*3)
    response = RedirectResponse(status_code=303, url="/home")
    response.set_cookie(
        key="skyndle_token",
        value=auth_jwt_token,
        httponly=True,
        samesite="lax"
    )

    return response

@router.get("/register")
async def get_register_page():
    """ Returns the registration page"""
    html_content = ""
    async with aiofiles.open("src/html/register.html", 'r') as file:
        html_content = await file.read()

    return HTMLResponse(content=html_content, status_code=200)

@router.post("/register")
def register_page(session=Depends(get_db_session), credentials: RegisterUser = Body(...)):
    """ Accepts the credentials & creates a new account"""

    db_credential = session.query(Credentials).filter(Credentials.email == credentials.email).first()
    if db_credential is not None:
        return JSONResponse(content={"message": "User already exists"}, status_code=403)
    
    # Create a new user
    now_time = datetime.utcnow()
    new_user = Users(email=credentials.email, user_name=credentials.user_name, created_at=now_time)
    new_user_db = session.add(new_user)
    new_cred = Credentials(email=credentials.email, password=credentials.password)
    new_user_db = session.add(new_cred)
    session.commit()

    return RedirectResponse(url="/auth/login", status_code=303)


