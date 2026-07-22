from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

PROBLEM_JSON = "application/problem+json"


class DomainError(Exception):
    """Base for domain failures mapped to RFC 9457 problem details (§6 API conventions)."""

    status = 400
    title = "Domain error"

    def __init__(self, detail: str):
        self.detail = detail


class NotFoundError(DomainError):
    status = 404
    title = "Not found"


def _problem(status: int, title: str, detail: str, type_: str = "about:blank") -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"type": type_, "title": title, "status": status, "detail": detail},
        media_type=PROBLEM_JSON,
    )


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return _problem(exc.status, exc.title, exc.detail)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _problem(exc.status_code, "HTTP error", str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem(422, "Validation failed", str(exc.errors()[:3]))
