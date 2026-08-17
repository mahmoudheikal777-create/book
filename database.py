"""
Database connection and initialization
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from config import DB_PATH


class Database:
    """Database connection manager"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with row factory"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Execute a SELECT query and return all results"""
        with self.get_connection() as conn:
            return conn.execute(query, params).fetchall()

    def execute_one(self, query: str, params: tuple = ()) -> sqlite3.Row | None:
        """Execute a query and return first result"""
        with self.get_connection() as conn:
            return conn.execute(query, params).fetchone()

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query, return lastrowid"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid

    def init_schema(self) -> None:
        """Initialize database schema"""
        with self.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS branches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    location TEXT NOT NULL,
                    open_hour INTEGER NOT NULL,
                    close_hour INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    price REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(branch_id) REFERENCES branches(id)
                );

                CREATE TABLE IF NOT EXISTS staff (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(branch_id) REFERENCES branches(id)
                );

                CREATE TABLE IF NOT EXISTS staff_services (
                    staff_id INTEGER NOT NULL,
                    service_id INTEGER NOT NULL,
                    PRIMARY KEY (staff_id, service_id),
                    FOREIGN KEY(staff_id) REFERENCES staff(id),
                    FOREIGN KEY(service_id) REFERENCES services(id)
                );

                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_code TEXT NOT NULL UNIQUE,
                    customer_id INTEGER NOT NULL,
                    branch_id INTEGER NOT NULL,
                    service_id INTEGER NOT NULL,
                    staff_id INTEGER NOT NULL,
                    booking_date TEXT NOT NULL,
                    booking_time TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'confirmed',
                    queue_number INTEGER NOT NULL,
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(customer_id) REFERENCES customers(id),
                    FOREIGN KEY(branch_id) REFERENCES branches(id),
                    FOREIGN KEY(service_id) REFERENCES services(id),
                    FOREIGN KEY(staff_id) REFERENCES staff(id)
                );

                CREATE TABLE IF NOT EXISTS queue_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_id INTEGER NOT NULL,
                    queue_date TEXT NOT NULL,
                    current_serving INTEGER NOT NULL DEFAULT 0,
                    last_updated TEXT NOT NULL,
                    UNIQUE(branch_id, queue_date),
                    FOREIGN KEY(branch_id) REFERENCES branches(id)
                );

                CREATE TABLE IF NOT EXISTS governorates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    country_code TEXT NOT NULL,
                    name_ar TEXT NOT NULL,
                    name_en TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS areas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    governorate_id INTEGER NOT NULL,
                    name_ar TEXT NOT NULL,
                    name_en TEXT NOT NULL,
                    FOREIGN KEY(governorate_id) REFERENCES governorates(id)
                );

                CREATE TABLE IF NOT EXISTS provider_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_id INTEGER,
                    provider_type TEXT NOT NULL,
                    service_mode TEXT NOT NULL,
                    display_name_ar TEXT NOT NULL,
                    display_name_en TEXT NOT NULL,
                    tagline_ar TEXT NOT NULL,
                    tagline_en TEXT NOT NULL,
                    bio_ar TEXT NOT NULL,
                    bio_en TEXT NOT NULL,
                    governorate_id INTEGER NOT NULL,
                    area_id INTEGER NOT NULL,
                    address_ar TEXT NOT NULL,
                    address_en TEXT NOT NULL,
                    lat REAL NOT NULL,
                    lng REAL NOT NULL,
                    chat_enabled INTEGER NOT NULL DEFAULT 1,
                    featured INTEGER NOT NULL DEFAULT 0,
                    verified INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(branch_id) REFERENCES branches(id),
                    FOREIGN KEY(governorate_id) REFERENCES governorates(id),
                    FOREIGN KEY(area_id) REFERENCES areas(id)
                );

                CREATE TABLE IF NOT EXISTS portfolio_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id INTEGER NOT NULL,
                    title_ar TEXT NOT NULL,
                    title_en TEXT NOT NULL,
                    category TEXT NOT NULL,
                    image_url TEXT NOT NULL,
                    FOREIGN KEY(provider_id) REFERENCES provider_profiles(id)
                );

                CREATE TABLE IF NOT EXISTS provider_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id INTEGER NOT NULL,
                    reviewer_name TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(provider_id) REFERENCES provider_profiles(id)
                );

                CREATE TABLE IF NOT EXISTS staff_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id INTEGER NOT NULL,
                    reviewer_name TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(staff_id) REFERENCES staff(id)
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id INTEGER NOT NULL,
                    sender_role TEXT NOT NULL,
                    sender_name TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    FOREIGN KEY(provider_id) REFERENCES provider_profiles(id)
                );

                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_bookings_branch_date 
                    ON bookings(branch_id, booking_date);
                CREATE INDEX IF NOT EXISTS idx_bookings_staff_date 
                    ON bookings(staff_id, booking_date);
                CREATE INDEX IF NOT EXISTS idx_customers_phone 
                    ON customers(phone);
                CREATE INDEX IF NOT EXISTS idx_staff_services 
                    ON staff_services(service_id, staff_id);
                CREATE INDEX IF NOT EXISTS idx_services_branch 
                    ON services(branch_id);
                CREATE INDEX IF NOT EXISTS idx_staff_branch 
                    ON staff(branch_id);
                """
            )


# Global database instance
db = Database()
