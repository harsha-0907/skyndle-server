
from fastapi import Request
from utils.jwt_utils import decode_jwt, JWTStatus
from utils.helper_functions import fetch_response
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse

class AuthRoute(APIRoute):
    def get_route_handler(self):
        parent_handler = super().get_route_handler()

        async def auth_handler(request: Request):
            # Validate the token
            auth_token = request.cookies.get("skyndle_token", None)

            if auth_token is None:
                # Token not present -> Redirect to Login
                return fetch_response(status_code=401)
            
            status, payload = decode_jwt(auth_token)
            if status == JWTStatus.INVALID:
                return fetch_response(status_code=401)

            elif status == JWTStatus.EXPIRED:
                response = fetch_response(status_code=428, is_json=True, data={"message": "Auth Token Expired"})
                custom_headers = {"X-Precondition-Action": "refresh-token", "X-Precondition-URL": "/auth/refresh"}
                response.headers.update(custom_headers)
                return response
            else:
                user_email = payload.get("user_email")
                request.state.user_email = user_email
                return await parent_handler(request)
                
        return auth_handler


