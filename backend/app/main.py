from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import traceback

# Load environment variables
load_dotenv()

from app.api.routes import router as api_router
from app.db.database import engine, Base
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# A10 / A02: Create all database tables on startup
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="FinRelief API", description="AI-Powered Debt Relief Platform")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# A02: Explicit CORS, never '*' when credentials are True
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000,http://127.0.0.1:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[url.strip() for url in FRONTEND_URL.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A02: Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# A10: Global Exception Handler to prevent 500 crashes returning raw stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full exception server-side
    print(f"Unhandled Exception on {request.url}:")
    traceback.print_exc()
    
    # Return a safe, generic error body to the client
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to FinRelief API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
