# In utils/decorators.py
import logging
from functools import wraps

def debug_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger()
        
        # Only run the detailed logging if the level is DEBUG
        if logger.getEffectiveLevel() == logging.DEBUG:
            handler_name = func.__module__.split('.')[-1]
            target = args[0] if args else "N/A"
            params = args[1] if len(args) > 1 else "N/A"

            logger.debug(f"--- Handler Debug: {handler_name} ---")
            logger.debug(f"  |-- Calling function: {func.__name__}")
            logger.debug(f"  |-- Target: '{target}'")
            logger.debug(f"  '-- Parameters: {params}")

            # Execute the original function (e.g., handle())
            result = func(*args, **kwargs)

            logger.debug(f"  |-- Raw Output: '{result}'")
            logger.debug(f"--- End Handler Debug ---")
            return result
        else:
            # If not in debug mode, just run the original function without extra logs
            return func(*args, **kwargs)
            
    return wrapper