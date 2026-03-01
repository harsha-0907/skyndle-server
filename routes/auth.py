
import aiofiles
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from datamodels.db import get_db_session, Credentials, Users
from utils.jwt_utils import encode_jwt, decode_jwt, JWTStatus
from datamodels.core_models import LoginCredentials, RegisterUser
from fastapi import APIRouter, Request, Body, Depends,Cookie
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

    if user_credential is None or user_credential.password != req_password:
        # Return a 401 response
        return JSONResponse(content={"message": "Invalid Credentials"}, status_code=401)
    
    # Valid Credentials
    reset_key = generate_id()
    reset_jwt_key = encode_jwt({"reset_key": reset_key}, expires_in=86400*7)

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

    user_credential.reset_key = reset_key
    user_credential.valid_upto = datetime.utcnow() + timedelta(days=7)
    session.commit()

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

@router.post("/logout")
def logout_user(request: Request, session=Depends(get_db_session)):
    """ Logging out the user from system """

    auth_token = request.cookies.get("skyndle_token", None)
    print(auth_token)
    if auth_token is None:
        return RedirectResponse(url="/auth/login", status_code=302)
        
    status, decoded_data = decode_jwt(auth_token)
    print(status, decoded_data)
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("skyndle_token")

    if status in (JWTStatus.OK, JWTStatus.EXPIRED):
        """ Remove the token from the DB """
        email = decoded_data["user_email"]
        cred = session.query(Credentials).filter(Credentials.email==email).first()
        cred.reset_key = None
        cred.valid_upto = None
        print(cred.__dict__)
        session.commit()
    
    return response

@router.post("/refresh")
def refresh_token(request: Request, session=Depends(get_db_session)):
    """ Refresh the auth token using reset_key """
    auth_token = request.cookies.get("skyndle_token", None)
    if auth_token is None:
        return JSONResponse(status_code=404, content={"status_code": 404, "message": "Resource Not Found"})
    
    status, decoded_data = decode_jwt(auth_token)
    if status == JWTStatus.OK:
        # Return response saying it is valid
        return JSONResponse(status_code=200, content={"status_code": 200, "message": "Token is valid"})
    
    elif status == JWTStatus.EXPIRED:
        # Check if the reset_key is valid
        user_email = decoded_data.get("user_email", None)
        reset_key = decoded_data["reset_key"]
        status, payload = decode_jwt(reset_key)

        if status in (JWTStatus.INVALID, JWTStatus.EXPIRED):
            # Remove the auth_key to logout the user
            response = JSONResponse(status_code=403, content={"status_code": 403, "message": "Un-Authorized Action"})
            response.delete_cookie(key="skyndle_token")
            return response

        # If the token is valid -> Check for the validity of the token & grant an extension
        cred = session.query(Credentials).filter(Credentials.email == user_email).first()

        valid_upto = None
        time_now = datetime.utcnow()

        if cred and cred.valid_upto:
            valid_upto = cred.valid_upto
        else:
            # Credential entry not found - DB has been cleared
            response = JSONResponse(status_code=403, content={"status_code": 403, "message": "Un-Authorized Action"})
            response.delete_cookie(key="skyndle_token")
            return response
        
        time_remaining = min(3600 * 3, int((valid_upto - time_now).total_seconds()))

        # If the reset_key is valid for more than 10 mins -> Grant an extension
        if time_remaining > 600:
            payload = {
                "user_email": user_email,
                "reset_key": reset_key,
                "session_id": generate_id()
            }
            auth_jwt_token = encode_jwt(payload, expires_in=time_remaining)
            response = JSONResponse(status_code=200, content={"status_code": 200, "message": "New Auth Token Generated"})
            response.set_cookie(key="skyndle_token", value=auth_jwt_token, samesite="lax")

            return response

        else:
            # Let the user login again
            response = JSONResponse(status_code=401, content={"message": "Auth Token Expired"})
            response.delete_cookie(key="skyndle_token")
            return response

    else:
        return JSONResponse(status_code=403, content={"status_code": 403, "message": "Un-Authorized Action."})
    
