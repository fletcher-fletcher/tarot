import random
import string
from datetime import datetime, time
from typing import Optional, List
import pytz


def generate_referral_code(user_id: int) -> str:
    """Generate referral code"""
    return f"{user_id}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"


def format_date(date: datetime) -> str:
    """Format datetime"""
    return date.strftime("%d.%m.%Y %H:%M")


def truncate_text(text: str, max_length: int = 4000) -> str:
    """Truncate text for Telegram message"""
    if not text:
        return text
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def smart_truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text without breaking words or paragraphs"""
    if not text:
        return text
    
    if len(text) <= max_length:
        return text
    
    # Truncate with space for suffix
    truncated = text[:max_length - len(suffix)]
    
    # Find last space to avoid breaking words
    last_space = truncated.rfind(' ')
    
    # Also try to find last paragraph break (double newline)
    last_paragraph = truncated.rfind('\n\n')
    
    if last_paragraph > max_length // 2:
        return truncated[:last_paragraph] + "\n\n" + suffix
    elif last_space > max_length // 2:
        return truncated[:last_space] + suffix
    else:
        return truncated + suffix


def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    if not text:
        return text
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))


def get_card_filename(card_id: str) -> str:
    """Get filename for card image"""
    return f"{card_id}.jpg"


def get_current_time_in_timezone(timezone_str: str) -> datetime:
    """Get current time in specified timezone"""
    try:
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz)
    except:
        return datetime.now()


def parse_time_string(time_str: str) -> Optional[time]:
    """Parse time string like '09:00' to time object"""
    try:
        hour, minute = map(int, time_str.split(":"))
        return time(hour, minute)
    except:
        return None