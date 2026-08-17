"""
Configuration and constants for Glow & Groom Booking Hub
"""
from pathlib import Path

# App Settings
APP_TITLE = "Glow & Groom Booking Hub"
APP_SUBTITLE = "نظام حجز صالونات عربي بتجربة أوضح، وتنقل أسهل، ولوحة تشغيل أبسط."
APP_ICON = "✂️"

# Database
DB_PATH = Path(__file__).with_name("salon_booking.db")

# Security
ADMIN_PIN = "1234"

# Language Settings
DEFAULT_LANGUAGE = "ar"
SUPPORTED_LANGUAGES = ["ar", "en"]

# UI/UX Settings
SIDEBAR_WIDTH = "wide"
LAYOUT = "wide"

# Time & Date
TIME_SLOT_INTERVAL = 30  # minutes
MIN_BOOKING_DAYS_AHEAD = 0  # can book today
MAX_BOOKING_DAYS_AHEAD = 90  # max 3 months

# Validation
MIN_PHONE_DIGITS = 10
MAX_PHONE_DIGITS = 15
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100

# Queue Settings
DEFAULT_QUEUE_STATUS = 1

# Messages
MESSAGES = {
    "ar": {
        "booking_success": "تم تأكيد الحجز بنجاح.",
        "invalid_phone": "يرجى إدخال رقم هاتف صحيح.",
        "invalid_name": "يرجى إدخال اسم صحيح.",
        "slot_unavailable": "هذا الموعد لم يعد متاحًا، اختر وقتًا آخر.",
        "past_date": "لا يمكن حجز موعد في تاريخ سابق.",
        "invalid_date": "تاريخ الحجز غير صالح.",
        "invalid_time": "وقت الحجز غير صالح.",
        "branch_not_found": "الفرع المختار غير موجود.",
        "service_not_found": "الخدمة المختارة غير موجودة.",
        "no_bookings_found": "لا توجد حجوزات مرتبطة بهذا الرقم.",
        "no_available_slots": "لا توجد مواعيد متاحة لهذا اليوم مع هذه الخدمة.",
        "full_capacity": "اختر يومًا آخر أو خدمة أخرى لوجود ازدحام كامل.",
        "wrong_pin": "الكود غير صحيح.",
        "queue_updated": "تم تحديث الدور الحالي إلى #{}.",
        "no_queue_data": "لا يوجد عملاء في قائمة الانتظار لهذا اليوم.",
    },
    "en": {
        "booking_success": "Booking confirmed successfully.",
        "invalid_phone": "Please enter a valid phone number.",
        "invalid_name": "Please enter a valid name.",
        "slot_unavailable": "This time slot is no longer available. Please choose another time.",
        "past_date": "Cannot book an appointment in the past.",
        "invalid_date": "Booking date is invalid.",
        "invalid_time": "Booking time is invalid.",
        "branch_not_found": "The selected branch was not found.",
        "service_not_found": "The selected service was not found.",
        "no_bookings_found": "No bookings found for this phone number.",
        "no_available_slots": "No available time slots for this service on this date.",
        "full_capacity": "Please choose another date or service due to full capacity.",
        "wrong_pin": "Invalid PIN code.",
        "queue_updated": "Queue status updated to #{}.",
        "no_queue_data": "No customers in queue for this date.",
    },
}


def get_message(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """Get localized message with optional formatting"""
    msg = MESSAGES.get(lang, MESSAGES[DEFAULT_LANGUAGE]).get(key, key)
    if kwargs:
        return msg.format(**kwargs)
    return msg
