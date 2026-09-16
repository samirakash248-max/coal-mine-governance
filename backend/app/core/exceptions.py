from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import ErrorResponse
import logging

logger = logging.getLogger(__name__)

class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

class NotFoundError(AppException):
    def __init__(self, detail: str = "Not Found", error_code: str = "NOT_FOUND"):
        super().__init__(status_code=404, detail=detail, error_code=error_code)

class ForbiddenError(AppException):
    def __init__(self, detail: str = "Forbidden", error_code: str = "FORBIDDEN"):
        super().__init__(status_code=403, detail=detail, error_code=error_code)

class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Unauthorized", error_code: str = "UNAUTHORIZED"):
        super().__init__(status_code=401, detail=detail, error_code=error_code)

class ConflictError(AppException):
    def __init__(self, detail: str = "Conflict", error_code: str = "CONFLICT"):
        super().__init__(status_code=409, detail=detail, error_code=error_code)

class ValidationError(AppException):
    def __init__(self, detail: str = "Validation Error", error_code: str = "VALIDATION_ERROR"):
        super().__init__(status_code=422, detail=detail, error_code=error_code)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(detail=exc.detail, error_code=exc.error_code).model_dump()
        )
        
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(detail="Invalid request parameters", error_code="VALIDATION_ERROR").model_dump()
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(detail="Internal database error", error_code="DATABASE_ERROR").model_dump()
        )
        
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(detail="Internal Server Error", error_code="INTERNAL_ERROR").model_dump()
        )
