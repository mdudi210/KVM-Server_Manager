# backend/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers
from backend.src.services import (
    adlogin,
    list_vms,
    login,
    register,
    vm_cloner,
    vm_creator,
    vm_events,
    vm_state_manager,
)

# Load environment variables from .env file
load_dotenv()

# ----------------------
# CORS Configuration
# ----------------------
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8080,http://127.0.0.1:8080,http://localhost,http://127.0.0.1",
)

# Split and clean the origins
origins = [origin.strip() for origin in ALLOWED_ORIGINS.split(",") if origin.strip()]

# If using '*', browsers reject credentials
allow_credentials = True
if "*" in origins:
    allow_credentials = False

# ----------------------
# FastAPI App
# ----------------------
app = FastAPI(
    title="KVM Server API",
    version="1.1.0",
    description="API for managing KVM servers",
)

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # dynamic origins
    allow_credentials=allow_credentials,
    allow_methods=["*"],           # allow all HTTP methods including OPTIONS
    allow_headers=["*"],           # allow all headers
)

# ----------------------
# Include routers
# ----------------------
app.include_router(vm_cloner.router, tags=["vm"])
app.include_router(vm_creator.router, tags=["vm"])
app.include_router(vm_state_manager.router, tags=["vm"])
app.include_router(vm_events.router, tags=["vm"])
app.include_router(list_vms.router, tags=["vm"])
app.include_router(login.router, tags=["auth"])
app.include_router(adlogin.router, tags=["auth"])
app.include_router(register.router, tags=["user"])

# ----------------------
# Root endpoint
# ----------------------
@app.get("/")
def read_root():
    return {"message": "KVM Server API is running"}

# ----------------------
# Run with Uvicorn
# ----------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
