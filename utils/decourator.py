import asyncio
import functools
import inspect
from typing import TypeVar, Callable, Optional, Type, Union, Any
from .logging import logger

T = TypeVar('T')

def async_retry(
    retries: int = 3,
    delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    A decorator for retrying async functions with exponential backoff.
    
    Args:
        retries (int): Maximum number of retries
        delay (float): Initial delay between retries in seconds
        max_delay (float): Maximum delay between retries in seconds
        exceptions (Exception | tuple[Exception]): Exception(s) to catch and retry on
        on_retry (Callable): Optional callback function called on each retry
        
    Example:
        @async_retry(retries=3, delay=1.0)
        async def my_function():
            pass
            
        @async_retry()
        @other_decorator
        async def decorated_function():
            pass
            
        class MyClass:
            @async_retry()
            async def my_method(self):
                pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Get the original function if it's already decorated
        original_func = getattr(func, '__wrapped__', func)
        
        # Check if the function is a coroutine
        is_coroutine = asyncio.iscoroutinefunction(original_func)
        if not is_coroutine:
            raise TypeError(f"Function {original_func.__name__} must be async")
        
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    if attempt == retries - 1:  # Last attempt
                        raise
                        
                    if on_retry:
                        on_retry(e, attempt + 1)
                    else:
                        logger.warning(
                            f"Retry {attempt + 1}/{retries} for {func.__name__} "
                            f"after error: {str(e)}"
                        )
                    
                    # Wait with exponential backoff
                    await asyncio.sleep(min(current_delay, max_delay))
                    current_delay *= 2
            
            # This should never happen due to the raise in the loop
            raise last_exception if last_exception else RuntimeError("Unexpected retry failure")
        
        # Preserve any existing attributes
        for attr_name, attr_value in inspect.getmembers(func):
            if not attr_name.startswith('__'):
                setattr(wrapper, attr_name, attr_value)
        
        return wrapper
    
    return decorator


# Example usage and tests
if __name__ == "__main__":
    class TestError(Exception):
        pass
    
    # Example with a simple async function
    @async_retry(retries=2, delay=0.1)
    async def test_function():
        raise TestError("Test error")
    
    # Example with multiple decorators
    @async_retry(retries=2, delay=0.1)
    @functools.lru_cache
    async def cached_function():
        raise TestError("Test error")
    
    # Example with a class method
    class TestClass:
        @async_retry(retries=2, delay=0.1)
        async def test_method(self):
            raise TestError("Test error")
        
        # Example with a static method
        @staticmethod
        @async_retry(retries=2, delay=0.1)
        async def test_static_method():
            raise TestError("Test error")
        
        # Example with a class method
        @classmethod
        @async_retry(retries=2, delay=0.1)
        async def test_class_method(cls):
            raise TestError("Test error")
    
    # Example with custom retry callback
    def on_retry_callback(error: Exception, attempt: int):
        print(f"Retry attempt {attempt} after error: {error}")
    
    @async_retry(retries=2, delay=0.1, on_retry=on_retry_callback)
    async def test_callback():
        raise TestError("Test error")
    
    async def run_tests():
        # Test simple function
        try:
            await test_function()
        except TestError:
            print("Simple function test passed")
        
        # Test cached function
        try:
            await cached_function()
        except TestError:
            print("Cached function test passed")
        
        # Test class method
        test_instance = TestClass()
        try:
            await test_instance.test_method()
        except TestError:
            print("Class method test passed")
        
        # Test static method
        try:
            await TestClass.test_static_method()
        except TestError:
            print("Static method test passed")
        
        # Test class method
        try:
            await TestClass.test_class_method()
        except TestError:
            print("Class method test passed")
        
        # Test callback
        try:
            await test_callback()
        except TestError:
            print("Callback test passed")
    
    # Run the tests
    if asyncio.get_event_loop().is_running():
        asyncio.create_task(run_tests())
    else:
        asyncio.run(run_tests())
