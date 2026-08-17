"""
Business logic and services layer
"""
import logging
from datetime import date, datetime, timedelta
from typing import Optional

from config import DEFAULT_QUEUE_STATUS, get_message
from database import db
from models import (
    Booking,
    BookingResult,
    Branch,
    Customer,
    DashboardSummary,
    QueueStatus,
    Service,
    Staff,
)
from utils import (
    CodeGenerator,
    DateTimeValidator,
    NameValidator,
    PhoneValidator,
    TimeSlotCalculator,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BranchService:
    \"\"\"Service for branch operations\"\"\"

    @staticmethod
    def get_all_branches() -> list[Branch]:
        \"\"\"Get all branches ordered by name\"\"\"
        try:
            rows = db.execute("SELECT * FROM branches ORDER BY name")
            return [Branch(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching branches: {e}")
            return []

    @staticmethod
    def get_branch(branch_id: int) -> Optional[Branch]:
        \"\"\"Get a single branch by ID\"\"\"
        try:
            row = db.execute_one("SELECT * FROM branches WHERE id = ?", (branch_id,))
            return Branch(**dict(row)) if row else None
        except Exception as e:
            logger.error(f"Error fetching branch {branch_id}: {e}")
            return None

    @staticmethod
    def get_branch_hours(branch_id: int) -> tuple[int, int]:
        \"\"\"Get opening and closing hours for a branch\"\"\"
        branch = BranchService.get_branch(branch_id)
        return (branch.open_hour, branch.close_hour) if branch else (10, 22)


class ServiceService:
    \"\"\"Service for service operations\"\"\"

    @staticmethod
    def get_services(branch_id: int) -> list[Service]:
        \"\"\"Get all services for a branch\"\"\"
        try:
            rows = db.execute(
                "SELECT * FROM services WHERE branch_id = ? ORDER BY name",
                (branch_id,),
            )
            return [Service(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching services for branch {branch_id}: {e}")
            return []

    @staticmethod
    def get_service(service_id: int) -> Optional[Service]:
        \"\"\"Get a single service by ID\"\"\"
        try:
            row = db.execute_one("SELECT * FROM services WHERE id = ?", (service_id,))
            return Service(**dict(row)) if row else None
        except Exception as e:
            logger.error(f"Error fetching service {service_id}: {e}")
            return None


class StaffService:
    \"\"\"Service for staff operations\"\"\"

    @staticmethod
    def get_staff_for_service(
        branch_id: int, service_id: int
    ) -> list[Staff]:
        \"\"\"Get all staff members who can provide a specific service\"\"\"
        try:
            rows = db.execute(
                \"\"\"
                SELECT DISTINCT staff.*
                FROM staff
                JOIN staff_services ON staff.id = staff_services.staff_id
                WHERE staff.branch_id = ? AND staff_services.service_id = ?
                ORDER BY staff.name
                \"\"\",
                (branch_id, service_id),
            )
            return [Staff(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(
                f"Error fetching staff for branch {branch_id}, service {service_id}: {e}"
            )
            return []

    @staticmethod
    def get_staff_bookings_for_day(staff_id: int, date_str: str) -> list[dict]:
        \"\"\"Get all confirmed bookings for a staff member on a specific day\"\"\"
        try:
            rows = db.execute(
                \"\"\"
                SELECT bookings.booking_time, services.duration_minutes
                FROM bookings
                JOIN services ON bookings.service_id = services.id
                WHERE bookings.staff_id = ?
                  AND bookings.booking_date = ?
                  AND bookings.status = 'confirmed'
                ORDER BY bookings.booking_time
                \"\"\",
                (staff_id, date_str),
            )
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(
                f"Error fetching bookings for staff {staff_id} on {date_str}: {e}"
            )
            return []


class TimeSlotService:
    \"\"\"Service for time slot operations\"\"\"

    @staticmethod
    def generate_available_slots(
        branch_id: int, service_id: int, date_str: str
    ) -> list[str]:
        \"\"\"Generate list of available time slots for a date and service\"\"\"
        try:
            # Validate date
            slot_date = DateTimeValidator.parse_date_str(date_str)
            if not slot_date or not DateTimeValidator.is_future_date(slot_date):
                return []

            # Get service and branch info
            service = ServiceService.get_service(service_id)
            if not service:
                return []

            open_hour, close_hour = BranchService.get_branch_hours(branch_id)

            # Generate all possible slots
            all_slots = TimeSlotCalculator.generate_slots(
                open_hour, close_hour, service.duration_minutes
            )

            # Filter to only available slots
            available = []
            for slot in all_slots:
                if TimeSlotService.is_slot_available(
                    branch_id, service_id, date_str, slot, service.duration_minutes
                ):
                    available.append(slot)

            return available
        except Exception as e:
            logger.error(
                f"Error generating slots for service {service_id} on {date_str}: {e}"
            )
            return []

    @staticmethod
    def is_slot_available(
        branch_id: int, service_id: int, date_str: str, time_str: str, duration_minutes: int
    ) -> bool:
        \"\"\"Check if a specific time slot is available\"\"\"
        try:
            staff_list = StaffService.get_staff_for_service(branch_id, service_id)
            if not staff_list:
                return False

            # Check if at least one staff member is available
            for staff in staff_list:
                if TimeSlotService.is_staff_slot_available(
                    staff.id, date_str, time_str, duration_minutes
                ):
                    return True

            return False
        except Exception as e:
            logger.error(
                f"Error checking slot availability on {date_str} at {time_str}: {e}"
            )
            return False

    @staticmethod
    def is_staff_slot_available(
        staff_id: int, date_str: str, time_str: str, duration_minutes: int
    ) -> bool:
        \"\"\"Check if a specific staff member is available at a time slot\"\"\"
        try:
            requested_slot = DateTimeValidator.parse_slot_datetime(date_str, time_str)
            if not requested_slot:
                return False

            bookings = StaffService.get_staff_bookings_for_day(staff_id, date_str)

            for booking in bookings:
                booked_slot = DateTimeValidator.parse_slot_datetime(
                    date_str, booking[\"booking_time\"]
                )
                if booked_slot and TimeSlotCalculator.check_overlap(
                    requested_slot, duration_minutes, booked_slot, booking[\"duration_minutes\"]
                ):
                    return False

            return True
        except Exception as e:
            logger.error(
                f\"Error checking staff availability for staff {staff_id}: {e}\"
            )
            return False

    @staticmethod
    def find_available_staff(
        branch_id: int, service_id: int, date_str: str, time_str: str, duration_minutes: int
    ) -> Optional[Staff]:
        \"\"\"Find first available staff member for a time slot\"\"\"
        try:
            staff_list = StaffService.get_staff_for_service(branch_id, service_id)
            for staff in staff_list:
                if TimeSlotService.is_staff_slot_available(staff.id, date_str, time_str, duration_minutes):
                    return staff
            return None
        except Exception as e:
            logger.error(f\"Error finding available staff: {e}\")
            return None


class CustomerService:
    \"\"\"Service for customer operations\"\"\"

    @staticmethod
    def upsert_customer(name: str, phone: str) -> Optional[int]:
        \"\"\"Create or update customer and return ID\"\"\"
        try:
            normalized_phone = PhoneValidator.normalize(phone)
            if not PhoneValidator.is_valid(normalized_phone):
                logger.warning(f\"Invalid phone: {phone}\")
                return None

            # Check if customer exists
            existing = db.execute_one(
                "SELECT id FROM customers WHERE phone = ?", (normalized_phone,)
            )

            if existing:
                # Update name if different
                db.execute_write(
                    "UPDATE customers SET full_name = ? WHERE id = ?",
                    (NameValidator.clean(name), existing[\"id\"]),
                )
                return existing[\"id\"]

            # Create new customer
            customer_id = db.execute_write(
                "INSERT INTO customers (full_name, phone) VALUES (?, ?)",
                (NameValidator.clean(name), normalized_phone),
            )
            return customer_id
        except Exception as e:
            logger.error(f\"Error upserting customer: {e}\")
            return None

    @staticmethod
    def get_customer_bookings(phone: str) -> list[Booking]:
        \"\"\"Get all bookings for a customer\"\"\"
        try:
            normalized_phone = PhoneValidator.normalize(phone)
            if not PhoneValidator.is_valid(normalized_phone):
                return []

            rows = db.execute(
                \"\"\"
                SELECT
                    b.id, b.booking_code, b.customer_id, b.branch_id, b.service_id,
                    b.staff_id, b.booking_date, b.booking_time, b.status, b.queue_number,
                    b.notes, b.created_at,
                    c.full_name AS customer_name, c.phone AS customer_phone,
                    br.name AS branch_name,
                    s.name AS service_name, s.price AS service_price,
                    st.name AS staff_name
                FROM bookings b
                JOIN customers c ON b.customer_id = c.id
                JOIN branches br ON b.branch_id = br.id
                JOIN services s ON b.service_id = s.id
                JOIN staff st ON b.staff_id = st.id
                WHERE c.phone = ?
                ORDER BY b.booking_date DESC, b.booking_time DESC
                \"\"\",
                (normalized_phone,),
            )

            return [Booking(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f\"Error fetching customer bookings: {e}\")
            return []


class BookingService:
    \"\"\"Service for booking operations\"\"\"

    @staticmethod
    def create_booking(
        name: str,
        phone: str,
        branch_id: int,
        service_id: int,
        date_str: str,
        time_str: str,
        notes: str = \"\",
        lang: str = \"ar\",
    ) -> BookingResult:
        \"\"\"Create a new booking with full validation\"\"\"
        try:
            # Validate inputs
            if not NameValidator.is_valid(name):
                return BookingResult(
                    False, get_message(\"invalid_name\", lang)
                )

            if not PhoneValidator.is_valid(phone):
                return BookingResult(
                    False, get_message(\"invalid_phone\", lang)
                )

            # Validate date
            booking_date = DateTimeValidator.parse_date_str(date_str)
            if not booking_date:
                return BookingResult(
                    False, get_message(\"invalid_date\", lang)
                )

            if not DateTimeValidator.is_future_date(booking_date):
                return BookingResult(
                    False, get_message(\"past_date\", lang)
                )

            # Validate time
            if not DateTimeValidator.is_valid_time_str(time_str):
                return BookingResult(
                    False, get_message(\"invalid_time\", lang)
                )

            # Validate branch and service exist
            branch = BranchService.get_branch(branch_id)
            service = ServiceService.get_service(service_id)

            if not branch or service.branch_id != branch_id:
                return BookingResult(
                    False, get_message(\"branch_not_found\", lang)
                )

            if not service or service.branch_id != branch_id:
                return BookingResult(
                    False, get_message(\"service_not_found\", lang)
                )

            # Find available staff
            available_staff = TimeSlotService.find_available_staff(
                branch_id, service_id, date_str, time_str, service.duration_minutes
            )

            if not available_staff:
                return BookingResult(
                    False, get_message(\"slot_unavailable\", lang)
                )

            # Create customer
            customer_id = CustomerService.upsert_customer(name, phone)
            if not customer_id:
                return BookingResult(
                    False, get_message(\"invalid_phone\", lang)
                )

            # Generate booking code and queue number
            all_bookings_count = db.execute_one(
                \"SELECT COUNT(*) AS cnt FROM bookings WHERE branch_id = ? AND booking_date = ?\",
                (branch_id, date_str),
            )[\"cnt\"]
            queue_number = all_bookings_count + 1
            booking_code = CodeGenerator.generate_booking_code(date_str, queue_number)
            created_at = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")

            # Create booking in database
            booking_id = db.execute_write(
                \"\"\"
                INSERT INTO bookings (
                    booking_code, customer_id, branch_id, service_id, staff_id,
                    booking_date, booking_time, queue_number, notes, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                \"\"\",
                (
                    booking_code,
                    customer_id,
                    branch_id,
                    service_id,
                    available_staff.id,
                    date_str,
                    time_str,
                    queue_number,
                    notes.strip(),
                    created_at,
                ),
            )

            # Initialize queue status if needed
            QueueService.ensure_queue_status(branch_id, date_str)

            logger.info(f\"Booking created: {booking_code}\")

            return BookingResult(
                True,
                get_message(\"booking_success\", lang),
                {
                    \"booking_id\": booking_id,
                    \"booking_code\": booking_code,
                    \"queue_number\": queue_number,
                    \"staff_name\": available_staff.name,
                    \"service_name\": service.name,
                    \"price\": service.price,
                    \"branch_name\": branch.name,
                    \"date\": date_str,
                    \"time\": time_str,
                },
            )
        except Exception as e:
            logger.error(f\"Error creating booking: {e}\")
            return BookingResult(False, \"حدث خطأ غير متوقع عند إنشاء الحجز.\" if lang == \"ar\" else \"An unexpected error occurred.\")

    @staticmethod
    def get_booking(booking_id: int) -> Optional[Booking]:
        \"\"\"Get a single booking by ID\"\"\"
        try:
            row = db.execute_one(\"SELECT * FROM bookings WHERE id = ?\", (booking_id,))
            return Booking(**dict(row)) if row else None
        except Exception as e:
            logger.error(f\"Error fetching booking {booking_id}: {e}\")
            return None

    @staticmethod
    def get_branch_bookings(branch_id: int, date_str: str) -> list[Booking]:
        \"\"\"Get all bookings for a branch on a specific date\"\"\"
        try:
            rows = db.execute(
                \"\"\"
                SELECT
                    b.id, b.booking_code, b.customer_id, b.branch_id, b.service_id,
                    b.staff_id, b.booking_date, b.booking_time, b.status, b.queue_number,
                    b.notes, b.created_at,
                    c.full_name AS customer_name, c.phone AS customer_phone,
                    br.name AS branch_name,
                    s.name AS service_name, s.price AS service_price, s.duration_minutes,
                    st.name AS staff_name
                FROM bookings b
                JOIN customers c ON b.customer_id = c.id
                JOIN branches br ON b.branch_id = br.id
                JOIN services s ON b.service_id = s.id
                JOIN staff st ON b.staff_id = st.id
                WHERE b.branch_id = ? AND b.booking_date = ?
                ORDER BY b.booking_date, b.booking_time, b.queue_number
                \"\"\",
                (branch_id, date_str),
            )

            return [Booking(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f\"Error fetching bookings for branch {branch_id}: {e}\")
            return []


class QueueService:
    \"\"\"Service for queue operations\"\"\"

    @staticmethod
    def get_queue_status(branch_id: int, date_str: str) -> int:
        \"\"\"Get current queue number being served\"\"\"
        try:
            row = db.execute_one(
                \"SELECT current_serving FROM queue_status WHERE branch_id = ? AND queue_date = ?\",
                (branch_id, date_str),
            )
            return row[\"current_serving\"] if row else DEFAULT_QUEUE_STATUS
        except Exception as e:
            logger.error(f\"Error fetching queue status: {e}\")
            return DEFAULT_QUEUE_STATUS

    @staticmethod
    def set_queue_status(branch_id: int, date_str: str, current_serving: int) -> bool:
        \"\"\"Update current queue number\"\"\"
        try:
            timestamp = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")
            db.execute_write(
                \"\"\"
                INSERT INTO queue_status (branch_id, queue_date, current_serving, last_updated)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(branch_id, queue_date)
                DO UPDATE SET current_serving = excluded.current_serving,
                              last_updated = excluded.last_updated
                \"\"\",
                (branch_id, date_str, current_serving, timestamp),
            )
            logger.info(f\"Queue status updated for branch {branch_id} on {date_str} to {current_serving}\")
            return True
        except Exception as e:
            logger.error(f\"Error updating queue status: {e}\")
            return False

    @staticmethod
    def ensure_queue_status(branch_id: int, date_str: str) -> None:
        \"\"\"Ensure queue status exists for a branch and date\"\"\"
        try:
            existing = db.execute_one(
                \"SELECT id FROM queue_status WHERE branch_id = ? AND queue_date = ?\",
                (branch_id, date_str),
            )
            if not existing:
                QueueService.set_queue_status(branch_id, date_str, DEFAULT_QUEUE_STATUS)
        except Exception as e:
            logger.error(f\"Error ensuring queue status: {e}\")


class DashboardService:
    \"\"\"Service for dashboard data\"\"\"

    @staticmethod
    def get_dashboard_summary(date_str: str) -> DashboardSummary:
        \"\"\"Get dashboard summary for a specific date\"\"\"
        try:
            # Total bookings and revenue
            booking_stats = db.execute_one(
                \"\"\"
                SELECT
                    COUNT(*) AS total_bookings,
                    COALESCE(SUM(s.price), 0) AS estimated_revenue
                FROM bookings b
                JOIN services s ON b.service_id = s.id
                WHERE b.booking_date = ?
                \"\"\",
                (date_str,),
            )

            # Waiting customers
            waiting = db.execute_one(
                \"\"\"
                SELECT COUNT(*) AS waiting_count
                FROM bookings b
                JOIN queue_status q
                  ON b.branch_id = q.branch_id AND b.booking_date = q.queue_date
                WHERE b.booking_date = ? AND b.queue_number >= q.current_serving
                \"\"\",
                (date_str,),
            )

            # Branch count
            branch_count = db.execute_one(\"SELECT COUNT(*) AS cnt FROM branches\")[\"cnt\"]

            return DashboardSummary(
                total_bookings=booking_stats[\"total_bookings\"],
                estimated_revenue=booking_stats[\"estimated_revenue\"],
                waiting_count=waiting[\"waiting_count\"] if waiting else 0,
                branch_count=branch_count,
            )
        except Exception as e:
            logger.error(f\"Error getting dashboard summary: {e}\")
            return DashboardSummary(0, 0.0, 0, 0)
