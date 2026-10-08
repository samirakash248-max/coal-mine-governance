import re
filepath = "backend/app/main.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

imports_target = "import uvicorn"
imports_replacement = """import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware"""

content = content.replace(imports_target, imports_replacement)

app_target = """app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Backend for the CoalMine governance platform.",
    lifespan=lifespan
)"""

app_replacement = """limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Backend for the CoalMine governance platform.",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)"""

content = content.replace(app_target, app_replacement)

headers_target = """        if hasattr(response, "headers"):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains\""""

headers_replacement = """        if hasattr(response, "headers"):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https: wss:"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin\""""

content = content.replace(headers_target, headers_replacement)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
