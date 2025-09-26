from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            return await self._handle_exception(request, e)
    
    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle different types of exceptions"""
        request_id = getattr(request.state, "request_id", "unknown")
        
        # HTTPException - already handled by FastAPI, but log it
        if isinstance(exc, HTTPException):
            logger.warning(
                "HTTP exception occurred",
                extra={
                    "request_id": request_id,
                    "status_code": exc.status_code,
                    "detail": exc.detail,
                    "url": str(request.url)
                }
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": "HTTP Error",
                    "detail": exc.detail,
                    "request_id": request_id
                }
            )
        
        # Database errors
        elif isinstance(exc, IntegrityError):
            logger.error(
                "Database integrity error",
                extra={
                    "request_id": request_id,
                    "error": str(exc),
                    "url": str(request.url)
                },
                exc_info=True
            )
            return JSONResponse(
                status_code=409,
                content={
                    "error": "Conflict",
                    "detail": "Data integrity constraint violation",
                    "request_id": request_id
                }
            )
        
        elif isinstance(exc, SQLAlchemyError):
            logger.error(
                "Database error",
                extra={
                    "request_id": request_id,
                    "error": str(exc),
                    "url": str(request.url)
                },
                exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Database Error",
                    "detail": "An error occurred while accessing the database",
                    "request_id": request_id
                }
            )
        
        # Validation errors
        elif isinstance(exc, ValidationError):
            logger.warning(
                "Validation error",
                extra={
                    "request_id": request_id,
                    "errors": exc.errors(),
                    "url": str(request.url)
                }
            )
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Validation Error",
                    "detail": exc.errors(),
                    "request_id": request_id
                }
            )
        
        # Generic server errors
        else:
            logger.error(
                "Unhandled exception",
                extra={
                    "request_id": request_id,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "url": str(request.url)
                },
                exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                    "request_id": request_id
                }
            )
