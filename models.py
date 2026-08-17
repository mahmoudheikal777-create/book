"""
Data models for the booking system
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Branch:
    \"\"\"Branch/Salon model\"\"\"
    id: int
    name: str
    category: str  # e.g., \"Beauty & Hair\", \"Barber Shop\"
    location: str
    open_hour: int
    close_hour: int
    created_at: Optional[str] = None

    def hours_display(self) -> str:
        return f\"{self.open_hour}:00 - {self.close_hour}:00\"


@dataclass
class Service:
    \"\"\"Service model\"\"\"
    id: int
    branch_id: int
    name: str
    duration_minutes: int
    price: float
    created_at: Optional[str] = None

    def price_display(self) -> str:
        return f\"{self.price:.0f} EGP\"

    def duration_display(self) -> str:
        return f\"{self.duration_minutes} دقيقة\"


@dataclass
class Staff:
    \"\"\"Staff member model\"\"\"
    id: int
    branch_id: int
    name: str
    title: str
    created_at: Optional[str] = None


@dataclass
class Customer:
    \"\"\"Customer model\"\"\"
    id: int
    full_name: str
    phone: str
    created_at: Optional[str] = None


@dataclass
class Booking:
    \"\"\"Booking model\"\"\"
    id: int
    booking_code: str
    customer_id: int
    branch_id: int
    service_id: int
    staff_id: int
    booking_date: str  # YYYY-MM-DD
    booking_time: str  # HH:MM AM/PM
    status: str  # confirmed, completed, cancelled
    queue_number: int
    notes: str = \"\"
    created_at: Optional[str] = None

    # Related data (from joins)
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    branch_name: Optional[str] = None
    service_name: Optional[str] = None
    service_price: Optional[float] = None
    duration_minutes: Optional[int] = None
    staff_name: Optional[str] = None

    def is_past(self) -> bool:
        \"\"\"Check if booking is in the past\"\"\"
        try:
            booking_dt = datetime.strptime(
                f\"{self.booking_date} {self.booking_time}\", \"%Y-%m-%d %I:%M %p\"
            )
            return booking_dt < datetime.now()
        except ValueError:
            return False

    def display_datetime(self) -> str:
        return f\"{self.booking_date} - {self.booking_time}\"


@dataclass
class QueueStatus:
    \"\"\"Queue status model\"\"\"
    id: int
    branch_id: int
    queue_date: str
    current_serving: int
    last_updated: str

    def waiting_count(self, total_bookings: int) -> int:
        return max(0, total_bookings - self.current_serving + 1)


@dataclass
class BookingResult:
    \"\"\"Result of a booking operation\"\"\"
    success: bool
    message: str
    booking_details: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            \"success\": self.success,
            \"message\": self.message,
            \"details\": self.booking_details or {},
        }


@dataclass
class DashboardSummary:
    \"\"\"Dashboard summary data\"\"\"
    total_bookings: int
    estimated_revenue: float
    waiting_count: int
    branch_count: int
    current_queue_number: int = 1
