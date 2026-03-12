import logging
import time
from typing import Callable

from fastapi import Request, Response


logger = logging.getLogger("fitness_diary")


async def logging_middleware(request: Request, call_next: Callable[[Request], Response]) -> Response:
    start_time = time.perf_counter()
    response: Response | None = None
    try:
        response = await call_next(request)
        return response
    finally:
        process_time = (time.perf_counter() - start_time) * 1000
        status_code = response.status_code if response is not None else 500
        logger.info(
            "%s %s - %d - %.2fms",
            request.method,
            request.url.path,
            status_code,
            process_time,
        )

