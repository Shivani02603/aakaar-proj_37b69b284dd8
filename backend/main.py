import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import ValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
from contextlib import asynccontextmanager

from database.config import init_db
from backend.routers.auth import router as auth_router
from backend.routers.observability import router as observability_router
from backend.routers.performance import router as performance_router
from backend.routers.scalability import router as scalability_router
from backend.routers.security import router as security_router
from backend.routers.sessions import router as sessions_router
from backend.routers.users import router as users_router

# Initialize FastAPI app
app = FastAPI(
    title="Aakaar Project",
    description="Backend API for Aakaar Project",
    version="1.0.0",
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SlowAPI rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse({"detail": str(exc)}, status_code=429)

app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse({"detail": exc.errors()}, status_code=422)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse({"detail": "Internal server error"}, status_code=500)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Mount routers
app.include_router(auth_router, prefix='/api/auth', tags=['Auth'])
app.include_router(observability_router, prefix='/api', tags=['Observability'])
app.include_router(performance_router, prefix='/api', tags=['Performance'])
app.include_router(scalability_router, prefix='/api/chat/sessions', tags=['Scalability'])
app.include_router(security_router, prefix='/api', tags=['Security'])
app.include_router(sessions_router, prefix='/api/chat/sessions', tags=['Sessions'])
app.include_router(users_router, prefix='/api/chat/sessions', tags=['Users'])

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # Perform any cleanup tasks here

app.router.lifespan_context = lifespan

# AI_ROUTER_INJECTION_POINT — do not remove this line
# AI layer — mounted by Agent 8B
from ai.routes import router as ai_router
app.include_router(ai_router, prefix='/api/ai', tags=['AI'])
