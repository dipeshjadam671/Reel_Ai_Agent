import asyncio
import functools
from typing import Callable, Type, Tuple
from backend.app.core.logging import logger

def async_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{max_retries} failed for {func.__name__}: {str(e)}. Retrying in {delay}s...",
                        extra={"event": "retry", "status": "retry_pending", "duration": 0, "cost": 0}
                    )
                    if attempt == max_retries:
                        break
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
            raise last_exception
        return wrapper
    return decorator
