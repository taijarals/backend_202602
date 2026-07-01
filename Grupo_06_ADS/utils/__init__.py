"""Utils package initialization."""
from .helpers import (
    validate_uuid, format_datetime, time_ago,
    calculate_percentage, get_difficulty_points,
    get_level_for_points, sanitize_input,
    generate_random_code, calculate_team_score,
    determine_grade, format_points, truncate_text,
    get_difficulty_color, get_status_color,
    validate_email, validate_password,
    calculate_remaining_time
)
from .exceptions import (
    BaseAppException, NotFoundError, UnauthorizedError,
    ForbiddenError, BadRequestError, ConflictError,
    ValidationError, DatabaseError, ExternalServiceError,
    handle_exception
)

__all__ = [
    'validate_uuid', 'format_datetime', 'time_ago',
    'calculate_percentage', 'get_difficulty_points',
    'get_level_for_points', 'sanitize_input',
    'generate_random_code', 'calculate_team_score',
    'determine_grade', 'format_points', 'truncate_text',
    'get_difficulty_color', 'get_status_color',
    'validate_email', 'validate_password',
    'calculate_remaining_time',
    'BaseAppException', 'NotFoundError', 'UnauthorizedError',
    'ForbiddenError', 'BadRequestError', 'ConflictError',
    'ValidationError', 'DatabaseError', 'ExternalServiceError',
    'handle_exception'
]
