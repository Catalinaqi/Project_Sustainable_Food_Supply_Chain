from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from functools import wraps
import logging
from datetime import datetime


class SafetyViolationError(Exception):
    """Exception raised for safety violations."""
    pass


class SafetyEnforcer:
    """
    Class to enforce safety rules before and after function execution.
    """

    def __init__(self) -> None:
        self.safety_violations: List[Dict[str, Any]] = []
        self.safety_rules: Dict[str, Union[Tuple[float, float], float, int]] = {
            'temperature_range': (-5.0, 30.0),  # Celsius
            'humidity_range': (30.0, 75.0),     # Percentage
            'max_transit_time': 72,              # Hours
            'min_quality_score': 0.7,            # Quality threshold
            'max_co2_emissions': 1000.0,         # kg CO2 equivalent
        }
        self.logger = logging.getLogger(__name__)

    def enforce_safety(self, operation_type: str = 'default') -> Callable[..., Any]:
        """
        Decorator to enforce safety preconditions and postconditions.

        Args:
            operation_type: Type of operation for context (not used currently).

        Returns:
            Callable decorator.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                context = {
                    'operation_type': operation_type,
                    'timestamp': datetime.now(),
                    'args': args,
                    'kwargs': kwargs
                }
                try:
                    self._check_preconditions(context)
                    result = func(*args, **kwargs)
                    self._check_postconditions(result, context)
                    return result
                except SafetyViolationError as sve:
                    self.logger.error(f"Safety violation in '{func.__name__}': {str(sve)}")
                    self._record_violation(func.__name__, str(sve))
                    raise
                except Exception as exc:
                    self.logger.error(f"Unexpected error in '{func.__name__}': {str(exc)}")
                    raise
            return wrapper
        return decorator

    def _check_preconditions(self, context: Dict[str, Any]) -> None:
        """
        Verify safety preconditions based on input arguments.

        Args:
            context: Dictionary with function call context including kwargs.

        Raises:
            SafetyViolationError: If any safety rule is violated.
        """
        kwargs = context.get('kwargs', {})

        temperature = kwargs.get('temperature')
        if temperature is not None:
            min_temp, max_temp = self.safety_rules['temperature_range']
            if not (min_temp <= temperature <= max_temp):
                raise SafetyViolationError(
                    f"Temperature {temperature}°C outside safe range [{min_temp}, {max_temp}]°C"
                )

        humidity = kwargs.get('humidity')
        if humidity is not None:
            min_hum, max_hum = self.safety_rules['humidity_range']
            if not (min_hum <= humidity <= max_hum):
                raise SafetyViolationError(
                    f"Humidity {humidity}% outside safe range [{min_hum}, {max_hum}]%"
                )

        quality_score = kwargs.get('quality_score')
        if quality_score is not None:
            min_quality = self.safety_rules['min_quality_score']
            if quality_score < min_quality:
                raise SafetyViolationError(
                    f"Quality score {quality_score} below minimum threshold {min_quality}"
                )

        co2_emissions = kwargs.get('co2_emissions')
        if co2_emissions is not None:
            max_emissions = self.safety_rules['max_co2_emissions']
            if co2_emissions > max_emissions:
                raise SafetyViolationError(
                    f"CO2 emissions {co2_emissions} kg exceed max allowed {max_emissions} kg"
                )

    def _check_postconditions(self, result: Any, context: Dict[str, Any]) -> None:
        """
        Verify safety postconditions based on function result.

        Args:
            result: Function return value.
            context: Function call context.

        Raises:
            SafetyViolationError: If any safety rule is violated.
        """
        if isinstance(result, dict):
            quality_score = result.get('quality_score')
            if quality_score is not None:
                min_quality = self.safety_rules['min_quality_score']
                if quality_score < min_quality:
                    raise SafetyViolationError(
                        f"Result quality score {quality_score} below minimum threshold {min_quality}"
                    )

            temperature = result.get('temperature')
            if temperature is not None:
                min_temp, max_temp = self.safety_rules['temperature_range']
                if not (min_temp <= temperature <= max_temp):
                    raise SafetyViolationError(
                        f"Result temperature {temperature}°C outside safe range [{min_temp}, {max_temp}]°C"
                    )

    def _record_violation(self, operation: str, error: str) -> None:
        """
        Record a safety violation event.

        Args:
            operation: Name of the operation/function.
            error: Description of the safety violation.
        """
        violation = {
            'timestamp': datetime.now(),
            'operation': operation,
            'error': error
        }
        self.safety_violations.append(violation)

    def get_safety_violations(self) -> List[Dict[str, Any]]:
        """
        Retrieve all recorded safety violations.

        Returns:
            List of safety violation dictionaries.
        """
        return self.safety_violations

    def update_safety_rule(self, rule_name: str, value: Union[Tuple[float, float], float, int]) -> None:
        """
        Update a safety rule value.

        Args:
            rule_name: The name of the safety rule to update.
            value: New value for the rule.

        Raises:
            ValueError: If the rule_name does not exist.
        """
        if rule_name not in self.safety_rules:
            raise ValueError(f"Unknown safety rule: {rule_name}")
        self.safety_rules[rule_name] = value
        self.logger.info(f"Updated safety rule '{rule_name}' to {value}")
