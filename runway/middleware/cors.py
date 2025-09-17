from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app: FastAPI) -> None:
    """Setup CORS middleware for the FastAPI application"""
    
    # Get allowed origins from environment or use defaults
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    # In development, allow all origins
    if os.getenv("ENVIRONMENT") == "development":
        allowed_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
        expose_headers=[
            "X-Total-Count",
            "X-Page-Count", 
            "X-Current-Page",
            "X-Per-Page"
        ]
    )
