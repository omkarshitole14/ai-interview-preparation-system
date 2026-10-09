from fastapi import Request
from fastapi.responses import JSONResponse


async def general_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred."
        },
    )