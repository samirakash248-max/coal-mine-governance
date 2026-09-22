import re

filepath = "backend/app/api/v1/auth.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = """@router.get("/google/login")
async def get_google_auth_url(settings: Settings = Depends(get_settings)):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured on the server")
    
    import secrets
    state = secrets.token_urlsafe(32)
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback\""""

replacement1 = """@router.get("/google/login")
async def get_google_auth_url(request: Request, settings: Settings = Depends(get_settings)):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured on the server")
    
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    
    frontend_url = settings.FRONTEND_URL
    if origin:
        frontend_url = origin.rstrip('/')
    elif referer:
        from urllib.parse import urlparse
        parsed = urlparse(referer)
        frontend_url = f"{parsed.scheme}://{parsed.netloc}"
        
    import secrets
    state = secrets.token_urlsafe(32)
    redirect_uri = f"{frontend_url}/auth/callback\""""

content = content.replace(target1, replacement1)

target2 = """    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured on the server")

    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback\""""

replacement2 = """    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured on the server")

    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    
    frontend_url = settings.FRONTEND_URL
    if origin:
        frontend_url = origin.rstrip('/')
    elif referer:
        from urllib.parse import urlparse
        parsed = urlparse(referer)
        frontend_url = f"{parsed.scheme}://{parsed.netloc}"
        
    redirect_uri = f"{frontend_url}/auth/callback\""""

content = content.replace(target2, replacement2)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
