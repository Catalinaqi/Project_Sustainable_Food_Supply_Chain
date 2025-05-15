from typing import Any, Callable, Dict, Optional
from functools import wraps
import asyncio
import time
import logging
from datetime import datetime

class GuaranteeResponseEnforcer:
    def __init__(self):
        self.response_violations = []
        self.timeout_limits = {
            'default': 5.0,                 # seconds
            'blockchain_operation': 30.0,    # longer timeout for blockchain operations
            'database_query': 3.0,          # database operations
            'product_validation': 2.0,      # product validation checks
            'quality_check': 4.0,           # quality control operations
            'sensor_data': 2.0             # IoT sensor data processing
        }
        self.logger = logging.getLogger(__name__)

    def enforce_response_time(self, operation_type: str = 'default') -> Callable:
        def decorator(function: Callable) -> Callable:
            @wraps(function)
            async def async_wrapper(*args, **kwargs) -> Any:
                timeout = self.timeout_limits.get(operation_type, self.timeout_limits['default'])
                start_time = time.time()
                
                try:
                    result = await asyncio.wait_for(
                        function(*args, **kwargs),
                        timeout=timeout
                    )
                    execution_time = time.time() - start_time
                    
                    self._log_execution_metrics(
                        function.__name__,
                        operation_type,
                        execution_time,
                        timeout
                    )
                    
                    return result
                
                except asyncio.TimeoutError:
                    execution_time = time.time() - start_time
                    self._record_violation(
                        function.__name__,
                        operation_type,
                        execution_time,
                        timeout
                    )
                    raise GuaranteeResponseError(
                        f"Operation {function.__name__} timed out after {timeout} seconds"
                    )

            @wraps(function)
            def sync_wrapper(*args, **kwargs) -> Any:
                timeout = self.timeout_limits.get(operation_type, self.timeout_limits['default'])
                start_time = time.time()
                
                try:
                    result = function(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if execution_time > timeout:
                        self._record_violation(
                            function.__name__,
                            operation_type,
                            execution_time,
                            timeout
                        )
                        raise GuaranteeResponseError(
                            f"Operation {function.__name__} exceeded timeout of {timeout} seconds"
                        )
                    
                    self._log_execution_metrics(
                        function.__name__,
                        operation_type,
                        execution_time,
                        timeout
                    )
                    
                    return result
                
                except Exception as e:
                    execution_time = time.time() - start_time
                    self._record_violation(
                        function.__name__,
                        operation_type,
                        execution_time,
                        timeout,
                        error=str(e)
                    )
                    raise

            return async_wrapper if asyncio.iscoroutinefunction(function) else sync_wrapper
        return decorator

    def _record_violation(self, 
                         function_name: str, 
                         operation_type: str, 
                         execution_time: float, 
                         timeout: float, 
                         error: Optional[str] = None) -> None:
        """Record a response time violation"""
        violation = {
            'timestamp': datetime.now(),
            'function': function_name,
            'operation_type': operation_type,
            'execution_time': execution_time,
            'timeout_limit': timeout,
            'error': error
        }
        self.response_violations.append(violation)
        self.logger.warning(
            f"Response time violation in {function_name}: "
            f"took {execution_time:.2f}s, limit was {timeout}s"
        )

    def _log_execution_metrics(self, 
                             function_name: str, 
                             operation_type: str, 
                             execution_time: float, 
                             timeout: float) -> None:
        """Log execution metrics for monitoring"""
        self.logger.info(
            f"Operation metrics - Function: {function_name}, "
            f"Type: {operation_type}, "
            f"Time: {execution_time:.2f}s, "
            f"Limit: {timeout}s"
        )

    def get_response_violations(self) -> list:
        """Return list of all response time violations"""
        return self.response_violations

    def update_timeout_limit(self, operation_type: str, timeout: float) -> None:
        """Update timeout limit for an operation type"""
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        self.timeout_limits[operation_type] = timeout
        self.logger.info(f"Updated timeout limit for {operation_type} to {timeout}s")

    def get_timeout_limit(self, operation_type: str) -> float:
        """Get timeout limit for an operation type"""
        return self.timeout_limits.get(operation_type, self.timeout_limits['default'])

class GuaranteeResponseError(Exception):
    pass
