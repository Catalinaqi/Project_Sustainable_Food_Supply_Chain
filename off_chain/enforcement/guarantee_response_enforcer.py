from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps
import asyncio
import time
import logging
from datetime import datetime


class GuaranteeResponseError(Exception):
    """Exception raised when a guaranteed response time is violated."""
    pass


class GuaranteeResponseEnforcer:
    """
    Class to enforce and log guaranteed response times on synchronous and asynchronous operations.
    """

    def __init__(self) -> None:
        self.response_violations: List[Dict[str, Any]] = []
        self.timeout_limits: Dict[str, float] = {
            'default': 5.0,                # seconds
            'blockchain_operation': 30.0,  # longer timeout for blockchain operations
            'database_query': 3.0,         # database operations
            'product_validation': 2.0,     # product validation checks
            'quality_check': 4.0,          # quality control operations
            'sensor_data': 2.0             # IoT sensor data processing
        }
        self.logger = logging.getLogger(__name__)

    def enforce_response_time(self, operation_type: str = 'default') -> Callable[..., Any]:
        """
        Decorator to enforce maximum response time for functions (sync or async).
        
        Args:
            operation_type: Type of operation to determine timeout limit.
            
        Returns:
            A decorator that wraps the function with timeout enforcement.
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            timeout_limit = self.timeout_limits.get(operation_type, self.timeout_limits['default'])

            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    start_time = time.perf_counter()
                    try:
                        result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_limit)
                        exec_time = time.perf_counter() - start_time
                        self._log_execution_metrics(func.__name__, operation_type, exec_time, timeout_limit)
                        return result
                    except asyncio.TimeoutError:
                        exec_time = time.perf_counter() - start_time
                        self._record_violation(func.__name__, operation_type, exec_time, timeout_limit)
                        raise GuaranteeResponseError(
                            f"Operation '{func.__name__}' timed out after {timeout_limit:.2f} seconds"
                        )
                return async_wrapper

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    exec_time = time.perf_counter() - start_time
                    if exec_time > timeout_limit:
                        self._record_violation(func.__name__, operation_type, exec_time, timeout_limit)
                        raise GuaranteeResponseError(
                            f"Operation '{func.__name__}' exceeded timeout limit of {timeout_limit:.2f} seconds"
                        )
                    self._log_execution_metrics(func.__name__, operation_type, exec_time, timeout_limit)
                    return result
                except Exception as exc:
                    exec_time = time.perf_counter() - start_time
                    self._record_violation(func.__name__, operation_type, exec_time, timeout_limit, error=str(exc))
                    raise
            return sync_wrapper

        return decorator

    def _record_violation(
        self,
        function_name: str,
        operation_type: str,
        execution_time: float,
        timeout_limit: float,
        error: Optional[str] = None
    ) -> None:
        """
        Record a response time violation and log a warning.
        
        Args:
            function_name: Name of the function where violation occurred.
            operation_type: Type of the operation.
            execution_time: Time the function took to execute.
            timeout_limit: Maximum allowed timeout.
            error: Optional error message associated with the violation.
        """
        violation = {
            'timestamp': datetime.now(),
            'function': function_name,
            'operation_type': operation_type,
            'execution_time': execution_time,
            'timeout_limit': timeout_limit,
            'error': error
        }
        self.response_violations.append(violation)
        self.logger.warning(
            f"Response time violation in '{function_name}': "
            f"execution took {execution_time:.3f}s (limit {timeout_limit:.3f}s). "
            + (f"Error: {error}" if error else "")
        )

    def _log_execution_metrics(
        self,
        function_name: str,
        operation_type: str,
        execution_time: float,
        timeout_limit: float
    ) -> None:
        """
        Log execution time metrics for monitoring purposes.
        
        Args:
            function_name: Name of the function executed.
            operation_type: Type of the operation.
            execution_time: Time taken to execute function.
            timeout_limit: Maximum allowed timeout.
        """
        self.logger.info(
            f"Operation metrics - Function: '{function_name}', "
            f"Type: '{operation_type}', "
            f"Execution Time: {execution_time:.3f}s, "
            f"Timeout Limit: {timeout_limit:.3f}s"
        )

    def get_response_violations(self) -> List[Dict[str, Any]]:
        """
        Retrieve all recorded response time violations.
        
        Returns:
            List of violation dictionaries.
        """
        return self.response_violations

    def update_timeout_limit(self, operation_type: str, timeout: float) -> None:
        """
        Update the timeout limit for a given operation type.
        
        Args:
            operation_type: The operation type to update.
            timeout: New timeout value in seconds (must be positive).
        
        Raises:
            ValueError: If timeout is not positive.
        """
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        self.timeout_limits[operation_type] = timeout
        self.logger.info(f"Updated timeout limit for '{operation_type}' to {timeout:.3f}s")

    def get_timeout_limit(self, operation_type: str) -> float:
        """
        Get the timeout limit for a given operation type.
        
        Args:
            operation_type: The operation type to query.
        
        Returns:
            Timeout limit in seconds.
        """
        return self.timeout_limits.get(operation_type, self.timeout_limits['default'])
