
from uuid import uuid4
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse

def fetch_response(status_code: int = 200, is_json: bool=True, data: dict = None, message:str = None):
    """ Returns a response message with status code and data"""
    html_page = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title> Skyndle </title>

        <style>
            :root {{
                --bg: #0f0f12;
                --card: #17171c;
                --gold: #c6a85a;
                --gold-soft: #a88c3f;
                --text: #e8e6e3;
                --muted: #9f9f9f;
                --link-hover: #d4b966;
            }}

            * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: "Segoe UI", sans-serif; }}

            body {{
                background: var(--bg);
                color: var(--text);
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 20px;
            }}

            .status-card {{
                background: var(--card);
                padding: 50px 40px;
                border-radius: 12px;
                width: 100%;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 0 30px rgba(198,168,90,0.15);
                border: 1px solid rgba(198,168,90,0.2);
            }}

            .status-code {{
                font-size: 72px;
                font-weight: 700;
                color: var(--gold);
                margin-bottom: 10px;
            }}

            .status-message {{
                font-size: 18px;
                color: var(--muted);
                margin-bottom: 30px;
                line-height: 1.5;
            }}

            .status-link {{
                display: inline-block;
                text-decoration: none;
                color: var(--gold);
                border: 1px solid var(--gold);
                padding: 12px 24px;
                border-radius: 8px;
                transition: all 0.3s ease;
                font-weight: 500;
            }}

            .status-link:hover {{
                background: var(--gold);
                color: #111;
                border-color: var(--gold-soft);
                box-shadow: 0 0 10px rgba(198,168,90,0.4);
            }}

            @media(max-width: 600px) {{
                .status-card {{ padding: 30px 20px; }}
                .status-code {{ font-size: 56px; }}
            }}
        </style>
        </head>

        <body>
            <div class="status-card">
                <div class="status-code">{0}</div>
                <div class="status-message">{1}</div>
                <a class="status-link" href="/home">Home</a>
            </div>
        </body>
        </html>
        """

    def response_401():
        return RedirectResponse(url="/auth/login", status_code=401)
    
    def response_403(is_json: bool, data: dict, message: str):
        if is_json:
            if data is None:
                data = {"status_code": 403,"message": "The Action is Un-Authorized"}
            
            return JSONResponse(content=data, status_code=403)
        
        else:
            if message is None:
                message = "The Action is Un-Authorized"
            
            return HTMLResponse(content=html_page.format(403, message), status_code=403)
    
    def response_404(is_json: bool, data: dict, message: str):
        if is_json:
            if data is None:
                data = {"status_code": 404,"message": "The Requested Resource is Not Found"}
            
            return JSONResponse(content=data, status_code=404)
        
        else:
            if message is None:
                message = "The Requested Resource is Not Found"
            
            return HTMLResponse(content=html_page.format(404, message), status_code=404)

    def response_xxx(status_code: int, is_json: bool, data: dict, message: str):
        if is_json:
            if data is None:
                data = {"status_code": status_code,"message": "Welcome to Skyndle"}

            return JSONResponse(content=data, status_code=status_code)
        else:
            if message is None:
                message = "Welcome to Skyndle"
            
            return HTMLResponse(content=html_page.format(status_code, message), status_code=status_code)
    
    if status_code == 401:
        return response_401()
    elif status_code == 403:
        return response_403(is_json, data, message)
    elif status_code == 404:
        return response_404(is_json, data, message)
    else:
        # Custom Message
        return response_xxx(status_code, is_json, data, message)

def generate_id():
    return str(uuid4())
