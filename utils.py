"""
Utility functions for validation and formatting
"""
import re
from datetime import date, datetime, time, timedelta
from typing import Optional

from config import (
    MAX_NAME_LENGTH,
    MAX_PHONE_DIGITS,
    MIN_NAME_LENGTH,
    MIN_PHONE_DIGITS,
)


class PhoneValidator:
    """Phone number validation and normalization"""

    @staticmethod
    def normalize(phone: str) -> str:
        """Extract only digits from phone number"""
        if not phone:
            return ""
        digits = "".join(ch for ch in phone if ch.isdigit())
        return digits

    @staticmethod
    def is_valid(phone: str) -> bool:
        """Check if phone number is valid"""
        digits = PhoneValidator.normalize(phone)
        return MIN_PHONE_DIGITS <= len(digits) <= MAX_PHONE_DIGITS

    @staticmethod
    def format_display(phone: str) -> str:
        """Format phone for display"""
        normalized = PhoneValidator.normalize(phone)
        if len(normalized) >= 10:
            return f"+20{normalized[-10:]}" if normalized.startswith("0") else f"+20{normalized}"
        return phone


class NameValidator:
    """Name validation"""

    @staticmethod
    def is_valid(name: str) -> bool:
        """Check if name is valid"""
        if not name:
            return False
        cleaned = name.strip()
        if not (MIN_NAME_LENGTH <= len(cleaned) <= MAX_NAME_LENGTH):
            return False
        # Allow Arabic, English, and spaces
        return bool(re.match(r"^[\u0600-\u06FF\u0750-\u077Fa-zA-Z\s'-]+$", cleaned))

    @staticmethod
    def clean(name: str) -> str:
        """Clean and normalize name"""
        return name.strip()


class DateTimeValidator:
    """Date and time validation"""

    @staticmethod
    def is_valid_date_str(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """Check if date string is in valid format"""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False

    @staticmethod
    def parse_date_str(date_str: str, format: str = "%Y-%m-%d") -> Optional[date]:
        """Parse date string safely"""
        try:
            return datetime.strptime(date_str, format).date()
        except ValueError:
            return None

    @staticmethod
    def is_valid_time_str(time_str: str, format: str = "%I:%M %p") -> bool:
        """Check if time string is in valid format"""
        try:
            datetime.strptime(time_str, format)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_future_date(date_obj: date, min_days_ahead: int = 0, max_days_ahead: int = 90) -> bool:
        """Check if date is within valid booking range"""
        today = date.today()
        min_date = today + timedelta(days=min_days_ahead)
        max_date = today + timedelta(days=max_days_ahead)
        return min_date <= date_obj <= max_date

    @staticmethod
    def parse_slot_datetime(date_str: str, time_str: str) -> Optional[datetime]:
        """Parse date and time into datetime safely"""
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
        except ValueError:
            return None


class TimeSlotCalculator:
    """Calculate available time slots"""

    @staticmethod
    def generate_slots(open_hour: int, close_hour: int, duration_minutes: int, 
                       slot_interval: int = 30) -> list[str]:
        """Generate available time slots for a day"""
        slots = []
        current = datetime.combine(date.today(), time(open_hour, 0))
        closing = datetime.combine(date.today(), time(close_hour, 0))

        while current + timedelta(minutes=duration_minutes) <= closing:
            slots.append(current.strftime("%I:%M %p"))
            current += timedelta(minutes=slot_interval)

        return slots

    @staticmethod
    def check_overlap(start1: datetime, duration1_min: int, start2: datetime, duration2_min: int) -> bool:
        """Check if two time slots overlap"""
        end1 = start1 + timedelta(minutes=duration1_min)
        end2 = start2 + timedelta(minutes=duration2_min)
        return start1 < end2 and end1 > start2


class CodeGenerator:
    """Generate unique codes"""

    @staticmethod
    def generate_booking_code(date_str: str, queue_number: int) -> str:
        """Generate booking code"""
        return f"BK-{date_str.replace('-', '')}-{queue_number:03d}"


class DataFormatter:
    """Format data for display"""

    @staticmethod
    def format_currency(amount: float, currency: str = "EGP") -> str:
        """Format currency"""
        return f"{amount:.0f} {currency}"

    @staticmethod
    def format_date_ar(date_obj: date | str) -> str:
        """Format date in Arabic"""
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        
        day_names = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
        month_names = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                       "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        
        return f"{day_names[date_obj.weekday()]} {date_obj.day} {month_names[date_obj.month - 1]} {date_obj.year}"

    @staticmethod
    def format_time_display(time_str: str) -> str:
        """Format time for display"""
        try:
            t = datetime.strptime(time_str, "%I:%M %p")
            return t.strftime("%H:%M")  # Convert to 24-hour format
        except ValueError:
            return time_str
