"""
Utility helper functions.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import re


def validate_uuid(value: str) -> bool:
    """Validate UUID string format."""
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """Format datetime to string."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    return dt.strftime(format_str)


def time_ago(dt: datetime) -> str:
    """Calculate time ago string."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))

    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 365:
        return f"{diff.days // 365} ano(s) atras"
    elif diff.days > 30:
        return f"{diff.days // 30} mes(es) atras"
    elif diff.days > 7:
        return f"{diff.days // 7} semana(s) atras"
    elif diff.days > 0:
        return f"{diff.days} dia(s) atras"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hora(s) atras"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minuto(s) atras"
    else:
        return "agora"


def calculate_percentage(current: int, total: int) -> float:
    """Calculate percentage."""
    if total == 0:
        return 0.0
    return round((current / total) * 100, 2)


def get_difficulty_points(difficulty: str) -> int:
    """Get default points for difficulty level."""
    difficulty_points = {
        "facil": 50,
        "media": 100,
        "dificil": 200,
        "expert": 500
    }
    return difficulty_points.get(difficulty, 100)


def get_level_for_points(points: int, levels: List[Dict]) -> Optional[Dict]:
    """Get level for given points."""
    current_level = levels[0] if levels else None
    for level in levels:
        if points >= level.get("pontos_necessarios", 0):
            current_level = level
        else:
            break
    return current_level


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input text."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Trim whitespace
    text = text.strip()
    # Truncate if needed
    if len(text) > max_length:
        text = text[:max_length]
    return text


def generate_random_code(length: int = 8) -> str:
    """Generate random alphanumeric code."""
    import secrets
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def calculate_team_score(members: List[Dict]) -> int:
    """Calculate team score from member scores."""
    return sum(m.get("aluno_pontos", 0) for m in members)


def determine_grade(score: int, max_score: int) -> tuple:
    """Determine grade and approval status."""
    if max_score == 0:
        return ("N/A", False)

    percentage = (score / max_score) * 100

    if percentage >= 90:
        return ("A", True)
    elif percentage >= 80:
        return ("B", True)
    elif percentage >= 70:
        return ("C", True)
    elif percentage >= 60:
        return ("D", True)
    else:
        return ("F", False)


def format_points(points: int) -> str:
    """Format points with thousands separator."""
    return f"{points:,}".replace(",", ".")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def get_difficulty_color(difficulty: str) -> str:
    """Get color for difficulty level."""
    colors = {
        "facil": "#10B981",
        "media": "#F59E0B",
        "dificil": "#EF4444",
        "expert": "#8B5CF6"
    }
    return colors.get(difficulty, "#8b98a5")


def get_status_color(status: str) -> str:
    """Get color for status."""
    colors = {
        "pendente": "#F59E0B",
        "em_progresso": "#3B82F6",
        "completa": "#10B981",
        "rejeitada": "#EF4444",
        "aprovada": "#10B981",
        "nota_atribuida": "#06B6D4"
    }
    return colors.get(status, "#8b98a5")


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 6:
        return (False, "A senha deve ter pelo menos 6 caracteres")
    return (True, "Senha valida")


def calculate_remaining_time(end_time: datetime) -> Dict[str, int]:
    """Calculate remaining time until deadline."""
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

    now = datetime.utcnow()
    diff = end_time - now

    if diff.total_seconds() <= 0:
        return {"days": 0, "hours": 0, "minutes": 0, "seconds": 0, "expired": True}

    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "expired": False
    }
