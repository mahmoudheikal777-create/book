import csv
import datetime as dt
import io
import sqlite3
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st


APP_TITLE = "Glow & Groom Booking Hub"
DB_PATH = Path(__file__).with_name("salon_booking.db")
ADMIN_PIN = "1234"


def normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    return digits if len(digits) >= 10 else (phone or "").strip()


def is_valid_phone(phone: str) -> bool:
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    return 10 <= len(digits) <= 15


def get_language() -> str:
    return st.session_state.get("lang", "ar")


def text(ar: str, en: str) -> str:
    return ar if get_language() == "ar" else en


def localized_value(ar_value: str | None, en_value: str | None) -> str:
    if get_language() == "ar":
        return ar_value or en_value or ""
    return en_value or ar_value or ""


def image_url(prompt: str, image_size: str = "landscape_4_3") -> str:
    return (
        "https://coresg-normal.trae.ai/api/ide/v1/text_to_image"
        f"?prompt={quote(prompt)}&image_size={image_size}"
    )


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                open_hour INTEGER NOT NULL,
                close_hour INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY(branch_id) REFERENCES branches(id)
            );

            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
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
                phone TEXT NOT NULL UNIQUE
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
            """
        )


def seed_demo_data() -> None:
    with connect_db() as conn:
        branch_count = conn.execute("SELECT COUNT(*) FROM branches").fetchone()[0]
        if branch_count == 0:
            branches = [
                ("Glow Lounge - Nasr City", "Beauty & Hair", "Nasr City", 10, 22),
                ("Royal Fade - Sheikh Zayed", "Barber Shop", "Sheikh Zayed", 12, 23),
                ("Pearl Beauty Studio - New Cairo", "Beauty Center", "New Cairo", 11, 21),
            ]

            branch_ids = []
            for branch in branches:
                cursor = conn.execute(
                    """
                    INSERT INTO branches (name, category, location, open_hour, close_hour)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    branch,
                )
                branch_ids.append(cursor.lastrowid)

            services_map = {
                branch_ids[0]: [
                    ("Haircut & Styling", 60, 220),
                    ("Hair Color Refresh", 90, 450),
                    ("Nail Care Session", 45, 180),
                    ("Skin Glow Treatment", 60, 300),
                ],
                branch_ids[1]: [
                    ("Classic Haircut", 45, 160),
                    ("Beard Design", 30, 110),
                    ("Premium Grooming", 60, 260),
                    ("Kids Cut", 30, 90),
                ],
                branch_ids[2]: [
                    ("Bridal Makeup Trial", 90, 550),
                    ("Facial Therapy", 60, 320),
                    ("Manicure & Pedicure", 75, 280),
                    ("Hair Spa", 60, 340),
                ],
            }

            service_ids = {}
            for branch_id, services in services_map.items():
                service_ids[branch_id] = []
                for service in services:
                    cursor = conn.execute(
                        """
                        INSERT INTO services (branch_id, name, duration_minutes, price)
                        VALUES (?, ?, ?, ?)
                        """,
                        (branch_id, *service),
                    )
                    service_ids[branch_id].append(cursor.lastrowid)

            staff_map = {
                branch_ids[0]: [
                    ("Maya Hassan", "Senior Stylist"),
                    ("Lina Adel", "Color Specialist"),
                    ("Sara Nabil", "Skin Therapist"),
                ],
                branch_ids[1]: [
                    ("Omar Essam", "Master Barber"),
                    ("Youssef Ashraf", "Beard Artist"),
                    ("Karim Samy", "Grooming Expert"),
                ],
                branch_ids[2]: [
                    ("Nadine Wael", "Makeup Artist"),
                    ("Salma Tarek", "Hair Specialist"),
                    ("Heba Sherif", "Beauty Therapist"),
                ],
            }

            staff_ids = {}
            for branch_id, employees in staff_map.items():
                staff_ids[branch_id] = []
                for employee in employees:
                    cursor = conn.execute(
                        """
                        INSERT INTO staff (branch_id, name, title)
                        VALUES (?, ?, ?)
                        """,
                        (branch_id, *employee),
                    )
                    staff_ids[branch_id].append(cursor.lastrowid)

            mappings = {
                branch_ids[0]: {
                    staff_ids[branch_ids[0]][0]: service_ids[branch_ids[0]][0:2],
                    staff_ids[branch_ids[0]][1]: service_ids[branch_ids[0]][1:3],
                    staff_ids[branch_ids[0]][2]: [service_ids[branch_ids[0]][2], service_ids[branch_ids[0]][3]],
                },
                branch_ids[1]: {
                    staff_ids[branch_ids[1]][0]: [service_ids[branch_ids[1]][0], service_ids[branch_ids[1]][2]],
                    staff_ids[branch_ids[1]][1]: [service_ids[branch_ids[1]][1], service_ids[branch_ids[1]][2]],
                    staff_ids[branch_ids[1]][2]: service_ids[branch_ids[1]],
                },
                branch_ids[2]: {
                    staff_ids[branch_ids[2]][0]: [service_ids[branch_ids[2]][0]],
                    staff_ids[branch_ids[2]][1]: [service_ids[branch_ids[2]][3], service_ids[branch_ids[2]][2]],
                    staff_ids[branch_ids[2]][2]: [service_ids[branch_ids[2]][1], service_ids[branch_ids[2]][2]],
                },
            }

            for branch_mapping in mappings.values():
                for staff_id, service_list in branch_mapping.items():
                    for service_id in service_list:
                        conn.execute(
                            """
                            INSERT INTO staff_services (staff_id, service_id)
                            VALUES (?, ?)
                            """,
                            (staff_id, service_id),
                        )

        governorate_count = conn.execute("SELECT COUNT(*) FROM governorates").fetchone()[0]
        if governorate_count == 0:
            governorates = [
                ("EG", "القاهرة", "Cairo"),
                ("EG", "الجيزة", "Giza"),
                ("EG", "الإسكندرية", "Alexandria"),
            ]
            governorate_ids = {}
            for gov in governorates:
                cursor = conn.execute(
                    """
                    INSERT INTO governorates (country_code, name_ar, name_en)
                    VALUES (?, ?, ?)
                    """,
                    gov,
                )
                governorate_ids[gov[2]] = cursor.lastrowid

            areas = [
                (governorate_ids["Cairo"], "مدينة نصر", "Nasr City"),
                (governorate_ids["Cairo"], "التجمع الخامس", "New Cairo"),
                (governorate_ids["Giza"], "الشيخ زايد", "Sheikh Zayed"),
                (governorate_ids["Giza"], "الدقي", "Dokki"),
                (governorate_ids["Alexandria"], "سموحة", "Smouha"),
                (governorate_ids["Alexandria"], "سان ستيفانو", "San Stefano"),
            ]
            for area in areas:
                conn.execute(
                    """
                    INSERT INTO areas (governorate_id, name_ar, name_en)
                    VALUES (?, ?, ?)
                    """,
                    area,
                )

        provider_count = conn.execute("SELECT COUNT(*) FROM provider_profiles").fetchone()[0]
        if provider_count == 0:
            branches = conn.execute("SELECT * FROM branches ORDER BY id").fetchall()
            areas = {
                row["name_en"]: row["id"]
                for row in conn.execute("SELECT id, name_en FROM areas").fetchall()
            }
            governorates = {
                row["name_en"]: row["id"]
                for row in conn.execute("SELECT id, name_en FROM governorates").fetchall()
            }

            branch_profiles = [
                (
                    branches[0]["id"],
                    "salon",
                    "in_salon",
                    "جلو لاونج",
                    "Glow Lounge",
                    "صالون متكامل للعناية بالشعر والبشرة والأظافر.",
                    "A full-service destination for hair, skin, and nail care.",
                    "فريق محترف وتجربة راقية مع خدمات تجميل متكاملة ومواعيد منظمة.",
                    "A polished salon team with premium beauty services and smooth booking flows.",
                    governorates["Cairo"],
                    areas["Nasr City"],
                    "مدينة نصر - القاهرة",
                    "Nasr City, Cairo",
                    30.0626,
                    31.3300,
                    1,
                    1,
                    1,
                ),
                (
                    branches[1]["id"],
                    "barbershop",
                    "in_salon",
                    "رويال فيد",
                    "Royal Fade",
                    "خبرة عالية في قصات الشعر والذقن والـ grooming.",
                    "Premium barbering with clean fades and grooming care.",
                    "صالون رجالي عصري مناسب للحجوزات السريعة والزيارات اليومية.",
                    "A modern barber destination built for fast appointments and daily visits.",
                    governorates["Giza"],
                    areas["Sheikh Zayed"],
                    "الشيخ زايد - الجيزة",
                    "Sheikh Zayed, Giza",
                    30.0131,
                    30.9754,
                    1,
                    1,
                    1,
                ),
                (
                    branches[2]["id"],
                    "beauty_center",
                    "in_salon",
                    "بيرل بيوتي ستوديو",
                    "Pearl Beauty Studio",
                    "مركز متخصص في المكياج والعناية والجلسات المميزة.",
                    "A beauty studio for makeup sessions and signature care.",
                    "يقدم جلسات متقدمة للعناية والجمال مع فريق نسائي متخصص.",
                    "Offers premium beauty treatments with a specialized female team.",
                    governorates["Cairo"],
                    areas["New Cairo"],
                    "التجمع الخامس - القاهرة",
                    "New Cairo, Cairo",
                    30.0094,
                    31.4204,
                    1,
                    1,
                    1,
                ),
                (
                    None,
                    "freelancer_barber",
                    "home_service",
                    "أحمد الحلاق الشخصي",
                    "Ahmed Personal Barber",
                    "حلاق متنقل لقص الشعر والذقن في المنزل.",
                    "Mobile barber for home haircut and beard styling.",
                    "يصل إلى العميل في المناطق المختارة ويقدم خدمة سريعة ومرنة.",
                    "Travels to clients in selected areas with flexible grooming sessions.",
                    governorates["Giza"],
                    areas["Dokki"],
                    "الدقي - الجيزة",
                    "Dokki, Giza",
                    30.0384,
                    31.2101,
                    1,
                    1,
                    1,
                ),
                (
                    None,
                    "freelancer_beauty",
                    "both",
                    "سارة بيوتي آرتست",
                    "Sara Beauty Artist",
                    "خبيرة تجميل شخصية للمناسبات والخدمات المنزلية.",
                    "Personal beauty artist for events and home visits.",
                    "تقدم جلسات مكياج وعناية شخصية ويمكن الحجز معها للمناسبات الخاصة.",
                    "Provides makeup and beauty sessions for private appointments and events.",
                    governorates["Alexandria"],
                    areas["Smouha"],
                    "سموحة - الإسكندرية",
                    "Smouha, Alexandria",
                    31.2156,
                    29.9553,
                    1,
                    1,
                    1,
                ),
            ]

            for profile in branch_profiles:
                conn.execute(
                    """
                    INSERT INTO provider_profiles (
                        branch_id, provider_type, service_mode, display_name_ar, display_name_en,
                        tagline_ar, tagline_en, bio_ar, bio_en, governorate_id, area_id,
                        address_ar, address_en, lat, lng, chat_enabled, featured, verified
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    profile,
                )

        portfolio_count = conn.execute("SELECT COUNT(*) FROM portfolio_items").fetchone()[0]
        if portfolio_count == 0:
            providers = conn.execute("SELECT id, display_name_en FROM provider_profiles").fetchall()
            portfolio_seed = {
                "Glow Lounge": [
                    (
                        "لوك شعر ناعم وانسيابي",
                        "Soft layered hairstyle",
                        "hair",
                        image_url(
                            "luxury beauty salon portfolio photo, female client with glossy layered hairstyle, soft studio lighting, realistic, editorial quality",
                            "portrait_4_3",
                        ),
                    ),
                    (
                        "جلسة عناية بالبشرة",
                        "Radiant skin treatment",
                        "skin",
                        image_url(
                            "professional skincare treatment in elegant salon room, glowing skin result, realistic website portfolio image",
                            "portrait_4_3",
                        ),
                    ),
                ],
                "Royal Fade": [
                    (
                        "فيد احترافي",
                        "Sharp skin fade",
                        "barber",
                        image_url(
                            "modern barber shop portfolio, sharp skin fade haircut on male client, realistic detail, premium lighting",
                            "portrait_4_3",
                        ),
                    ),
                    (
                        "تنسيق ذقن كلاسيكي",
                        "Classic beard shaping",
                        "barber",
                        image_url(
                            "barber grooming portfolio image, classic beard shaping and sharp haircut, realistic professional shot",
                            "portrait_4_3",
                        ),
                    ),
                ],
                "Pearl Beauty Studio": [
                    (
                        "مكياج مناسبات راق",
                        "Elegant bridal makeup",
                        "makeup",
                        image_url(
                            "beauty studio portfolio, elegant bridal makeup close-up, realistic, premium editorial style",
                            "portrait_4_3",
                        ),
                    ),
                    (
                        "جلسة عناية متقدمة",
                        "Premium beauty care session",
                        "beauty",
                        image_url(
                            "beauty center portfolio photo, premium facial and beauty care room, realistic website image",
                            "portrait_4_3",
                        ),
                    ),
                ],
                "Ahmed Personal Barber": [
                    (
                        "خدمة منزلية مريحة",
                        "At-home grooming setup",
                        "home_service",
                        image_url(
                            "mobile barber at home service portfolio image, professional grooming setup in client home, realistic",
                            "portrait_4_3",
                        ),
                    ),
                ],
                "Sara Beauty Artist": [
                    (
                        "مكياج شخصي متنقل",
                        "Mobile makeup session",
                        "makeup",
                        image_url(
                            "personal beauty artist portfolio, mobile makeup service for event, realistic glamorous portrait",
                            "portrait_4_3",
                        ),
                    ),
                ],
            }

            for provider in providers:
                for item in portfolio_seed.get(provider["display_name_en"], []):
                    conn.execute(
                        """
                        INSERT INTO portfolio_items (provider_id, title_ar, title_en, category, image_url)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (provider["id"], *item),
                    )

        review_count = conn.execute("SELECT COUNT(*) FROM provider_reviews").fetchone()[0]
        if review_count == 0:
            provider_names = {
                row["display_name_en"]: row["id"]
                for row in conn.execute("SELECT id, display_name_en FROM provider_profiles").fetchall()
            }
            provider_reviews = [
                (provider_names["Glow Lounge"], "Nour", 5, "Great service quality and smooth booking experience."),
                (provider_names["Glow Lounge"], "Mariam", 4, "Friendly staff and organized timing."),
                (provider_names["Royal Fade"], "Mostafa", 5, "Excellent barber skills and neat results."),
                (provider_names["Pearl Beauty Studio"], "Hana", 5, "Beautiful makeup result and professional team."),
                (provider_names["Ahmed Personal Barber"], "Karim", 4, "Convenient home service and good timing."),
                (provider_names["Sara Beauty Artist"], "Yasmin", 5, "Professional artist with great portfolio."),
            ]
            created_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for review in provider_reviews:
                conn.execute(
                    """
                    INSERT INTO provider_reviews (provider_id, reviewer_name, rating, comment, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (*review, created_at),
                )

        staff_review_count = conn.execute("SELECT COUNT(*) FROM staff_reviews").fetchone()[0]
        if staff_review_count == 0:
            staff_rows = conn.execute("SELECT id, name FROM staff").fetchall()
            ratings_by_name = {
                "Maya Hassan": [("Rana", 5, "Excellent styling and attention to detail.")],
                "Omar Essam": [("Ali", 5, "One of the best fades I tried.")],
                "Nadine Wael": [("Dina", 5, "Amazing makeup artist and very professional.")],
            }
            created_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for staff_row in staff_rows:
                for item in ratings_by_name.get(staff_row["name"], []):
                    conn.execute(
                        """
                        INSERT INTO staff_reviews (staff_id, reviewer_name, rating, comment, created_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (staff_row["id"], item[0], item[1], item[2], created_at),
                    )

        message_count = conn.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0]
        if message_count == 0:
            provider_names = {
                row["display_name_en"]: row["id"]
                for row in conn.execute("SELECT id, display_name_en FROM provider_profiles").fetchall()
            }
            now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            seed_messages = [
                (provider_names["Glow Lounge"], "client", "Mona", "Is there a late evening slot this week?", now),
                (provider_names["Glow Lounge"], "provider", "Glow Lounge Team", "Yes, there are evening slots available on Thursday.", now),
                (provider_names["Sara Beauty Artist"], "client", "Laila", "Do you offer bridal trial sessions?", now),
            ]
            for message in seed_messages:
                conn.execute(
                    """
                    INSERT INTO chat_messages (provider_id, sender_role, sender_name, message_text, sent_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    message,
                )


def fetch_all(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    with connect_db() as conn:
        return conn.execute(query, params).fetchall()


def fetch_one(query: str, params: tuple = ()) -> sqlite3.Row | None:
    with connect_db() as conn:
        return conn.execute(query, params).fetchone()


def get_branches() -> list[sqlite3.Row]:
    return fetch_all("SELECT * FROM branches ORDER BY name")


def get_services(branch_id: int) -> list[sqlite3.Row]:
    return fetch_all(
        "SELECT * FROM services WHERE branch_id = ? ORDER BY name",
        (branch_id,),
    )


def get_staff_for_service(branch_id: int, service_id: int) -> list[sqlite3.Row]:
    return fetch_all(
        """
        SELECT staff.*
        FROM staff
        JOIN staff_services ON staff.id = staff_services.staff_id
        WHERE staff.branch_id = ? AND staff_services.service_id = ?
        ORDER BY staff.name
        """,
        (branch_id, service_id),
    )


def get_bookings_with_details(branch_id: int | None = None, date_str: str | None = None) -> list[sqlite3.Row]:
    query = """
        SELECT
            bookings.*,
            customers.full_name AS customer_name,
            customers.phone AS customer_phone,
            branches.name AS branch_name,
            services.name AS service_name,
            services.price AS service_price,
            services.duration_minutes AS duration_minutes,
            staff.name AS staff_name
        FROM bookings
        JOIN customers ON bookings.customer_id = customers.id
        JOIN branches ON bookings.branch_id = branches.id
        JOIN services ON bookings.service_id = services.id
        JOIN staff ON bookings.staff_id = staff.id
        WHERE 1 = 1
    """
    params: list = []
    if branch_id is not None:
        query += " AND bookings.branch_id = ?"
        params.append(branch_id)
    if date_str is not None:
        query += " AND bookings.booking_date = ?"
        params.append(date_str)
    query += " ORDER BY bookings.booking_date, bookings.booking_time, bookings.queue_number"
    return fetch_all(query, tuple(params))


def get_customer_bookings(phone: str) -> list[sqlite3.Row]:
    normalized_phone = normalize_phone(phone)
    if not normalized_phone:
        return []

    raw_phone = normalized_phone
    search_phone = normalized_phone if is_valid_phone(normalized_phone) else phone.strip()
    return fetch_all(
        """
        SELECT
            bookings.booking_code,
            bookings.booking_date,
            bookings.booking_time,
            bookings.status,
            bookings.queue_number,
            branches.name AS branch_name,
            services.name AS service_name,
            staff.name AS staff_name
        FROM bookings
        JOIN customers ON bookings.customer_id = customers.id
        JOIN branches ON bookings.branch_id = branches.id
        JOIN services ON bookings.service_id = services.id
        JOIN staff ON bookings.staff_id = staff.id
        WHERE customers.phone = ? OR customers.phone = ?
        ORDER BY bookings.booking_date DESC, bookings.booking_time DESC
        """,
        (search_phone, raw_phone),
    )


def get_queue_status(branch_id: int, date_str: str) -> int:
    row = fetch_one(
        """
        SELECT current_serving
        FROM queue_status
        WHERE branch_id = ? AND queue_date = ?
        """,
        (branch_id, date_str),
    )
    return row["current_serving"] if row else 0


def set_queue_status(branch_id: int, date_str: str, current_serving: int) -> None:
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO queue_status (branch_id, queue_date, current_serving, last_updated)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(branch_id, queue_date)
            DO UPDATE SET current_serving = excluded.current_serving,
                          last_updated = excluded.last_updated
            """,
            (branch_id, date_str, current_serving, timestamp),
        )


def get_branch_hours(branch_id: int) -> tuple[int, int]:
    branch = fetch_one("SELECT open_hour, close_hour FROM branches WHERE id = ?", (branch_id,))
    return branch["open_hour"], branch["close_hour"]


def generate_time_slots(branch_id: int, duration_minutes: int, selected_date: dt.date) -> list[str]:
    open_hour, close_hour = get_branch_hours(branch_id)
    slot_cursor = dt.datetime.combine(selected_date, dt.time(open_hour, 0))
    closing_time = dt.datetime.combine(selected_date, dt.time(close_hour, 0))
    slots = []
    while slot_cursor + dt.timedelta(minutes=duration_minutes) <= closing_time:
        slots.append(slot_cursor.strftime("%I:%M %p"))
        slot_cursor += dt.timedelta(minutes=30)
    return slots


def parse_slot(date_str: str, time_str: str) -> dt.datetime:
    return dt.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")


def get_staff_bookings_for_day(staff_id: int, date_str: str) -> list[sqlite3.Row]:
    return fetch_all(
        """
        SELECT bookings.booking_time, services.duration_minutes
        FROM bookings
        JOIN services ON bookings.service_id = services.id
        WHERE bookings.staff_id = ? AND bookings.booking_date = ? AND bookings.status = 'confirmed'
        """,
        (staff_id, date_str),
    )


def is_slot_available(staff_id: int, date_str: str, time_str: str, duration_minutes: int) -> bool:
    requested_start = parse_slot(date_str, time_str)
    requested_end = requested_start + dt.timedelta(minutes=duration_minutes)

    for booking in get_staff_bookings_for_day(staff_id, date_str):
        booked_start = parse_slot(date_str, booking["booking_time"])
        booked_end = booked_start + dt.timedelta(minutes=booking["duration_minutes"])
        overlaps = requested_start < booked_end and requested_end > booked_start
        if overlaps:
            return False
    return True


def available_staff_for_slot(branch_id: int, service_id: int, date_str: str, time_str: str, duration_minutes: int) -> list[sqlite3.Row]:
    candidates = get_staff_for_service(branch_id, service_id)
    return [
        person
        for person in candidates
        if is_slot_available(person["id"], date_str, time_str, duration_minutes)
    ]


def build_available_slots(branch_id: int, service_id: int, date_str: str, duration_minutes: int) -> list[str]:
    selected_date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
    slots = generate_time_slots(branch_id, duration_minutes, selected_date)
    available = []
    for slot in slots:
        if available_staff_for_slot(branch_id, service_id, date_str, slot, duration_minutes):
            available.append(slot)
    return available


def upsert_customer(name: str, phone: str) -> int:
    cleaned_phone = normalize_phone(phone)
    with connect_db() as conn:
        customer = conn.execute(
            "SELECT id FROM customers WHERE phone = ?",
            (cleaned_phone,),
        ).fetchone()
        if customer:
            conn.execute(
                "UPDATE customers SET full_name = ? WHERE id = ?",
                (name, customer["id"]),
            )
            return customer["id"]

        cursor = conn.execute(
            "INSERT INTO customers (full_name, phone) VALUES (?, ?)",
            (name, cleaned_phone),
        )
        return cursor.lastrowid


def create_booking(
    name: str,
    phone: str,
    branch_id: int,
    service_id: int,
    date_str: str,
    time_str: str,
    notes: str = "",
) -> tuple[bool, str, dict]:
    cleaned_name = (name or "").strip()
    cleaned_phone = normalize_phone(phone)
    if not cleaned_name or not is_valid_phone(cleaned_phone):
        return False, "يرجى إدخال اسم صحيح ورقم هاتف صحيح.", {}

    try:
        selected_date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "تاريخ الحجز غير صالح.", {}

    if selected_date < dt.date.today():
        return False, "لا يمكن حجز موعد في تاريخ سابق.", {}

    branch = fetch_one("SELECT id, name FROM branches WHERE id = ?", (branch_id,))
    service = fetch_one(
        "SELECT id, name, duration_minutes, price FROM services WHERE id = ?",
        (service_id,),
    )
    if branch is None or service is None:
        return False, "الفرع أو الخدمة المختارة غير موجودة.", {}

    try:
        parse_slot(date_str, time_str)
    except ValueError:
        return False, "وقت الحجز غير صالح.", {}

    available_staff = available_staff_for_slot(
        branch_id,
        service_id,
        date_str,
        time_str,
        service["duration_minutes"],
    )
    if not available_staff:
        return False, "هذا الموعد لم يعد متاحًا، اختر وقتًا آخر.", {}

    assigned_staff = available_staff[0]
    customer_id = upsert_customer(cleaned_name, cleaned_phone)

    day_count = fetch_one(
        "SELECT COUNT(*) AS total FROM bookings WHERE branch_id = ? AND booking_date = ?",
        (branch_id, date_str),
    )["total"]
    queue_number = day_count + 1
    booking_code = f"BK-{date_str.replace('-', '')}-{queue_number:03d}"
    created_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO bookings (
                booking_code, customer_id, branch_id, service_id, staff_id,
                booking_date, booking_time, queue_number, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                booking_code,
                customer_id,
                branch_id,
                service_id,
                assigned_staff["id"],
                date_str,
                time_str,
                queue_number,
                notes.strip(),
                created_at,
            ),
        )

    if get_queue_status(branch_id, date_str) == 0:
        set_queue_status(branch_id, date_str, 1)

    return True, "تم تأكيد الحجز بنجاح.", {
        "booking_code": booking_code,
        "queue_number": queue_number,
        "staff_name": assigned_staff["name"],
        "service_name": service["name"],
        "price": service["price"],
        "branch_name": branch["name"],
        "date": date_str,
        "time": time_str,
    }


def get_dashboard_summary(date_str: str) -> dict:
    with connect_db() as conn:
        totals = conn.execute(
            """
            SELECT
                COUNT(*) AS total_bookings,
                COALESCE(SUM(services.price), 0) AS estimated_revenue
            FROM bookings
            JOIN services ON bookings.service_id = services.id
            WHERE bookings.booking_date = ?
            """,
            (date_str,),
        ).fetchone()

        waiting = conn.execute(
            """
            SELECT COUNT(*) AS waiting_count
            FROM bookings
            JOIN queue_status
              ON bookings.branch_id = queue_status.branch_id
             AND bookings.booking_date = queue_status.queue_date
            WHERE bookings.booking_date = ?
              AND bookings.queue_number >= queue_status.current_serving
            """,
            (date_str,),
        ).fetchone()

        branch_count = conn.execute("SELECT COUNT(*) AS total FROM branches").fetchone()

    return {
        "total_bookings": totals["total_bookings"],
        "estimated_revenue": totals["estimated_revenue"],
        "waiting_count": waiting["waiting_count"],
        "branch_count": branch_count["total"],
    }


def to_csv(rows: list[sqlite3.Row]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Booking Code",
            "Client Name",
            "Phone",
            "Branch",
            "Service",
            "Staff",
            "Date",
            "Time",
            "Queue",
            "Status",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["booking_code"],
                row["customer_name"],
                row["customer_phone"],
                row["branch_name"],
                row["service_name"],
                row["staff_name"],
                row["booking_date"],
                row["booking_time"],
                row["queue_number"],
                row["status"],
            ]
        )
    return output.getvalue()


def inject_style() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                direction: rtl;
                background:
                    radial-gradient(circle at top right, rgba(255, 255, 255, 0.55), transparent 25%),
                    linear-gradient(160deg, #f8fafc 0%, #eef2ff 46%, #fdf2f8 100%);
                color: #0f172a;
            }
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
                max-width: 1200px;
            }
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
                border-left: 1px solid rgba(255, 255, 255, 0.08);
            }
            section[data-testid="stSidebar"] * {
                color: #f8fafc !important;
            }
            .page-hero {
                background: linear-gradient(135deg, #111827 0%, #1e293b 45%, #312e81 100%);
                border-radius: 28px;
                padding: 1.6rem 1.6rem 1.4rem;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 24px 50px rgba(15, 23, 42, 0.16);
                margin-bottom: 1rem;
            }
            .page-hero h1 {
                margin: 0;
                font-size: 2.15rem;
                font-weight: 700;
            }
            .page-hero p {
                margin: 0.55rem 0 0;
                color: #dbeafe;
                line-height: 1.8;
            }
            .soft-card, .ticket-card {
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 22px;
                padding: 1.15rem 1.2rem;
                box-shadow: 0 16px 35px rgba(148, 163, 184, 0.14);
            }
            .ticket-card {
                background: linear-gradient(135deg, #eff6ff 0%, #fdf2f8 100%);
                border: 1px solid rgba(129, 140, 248, 0.2);
            }
            .section-title {
                font-size: 1.15rem;
                font-weight: 700;
                margin: 0 0 0.85rem;
                color: #0f172a;
            }
            .section-note {
                color: #475569;
                line-height: 1.7;
                margin-bottom: 0;
            }
            .mini-stat {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 18px;
                padding: 1rem 1.05rem;
                box-shadow: 0 10px 24px rgba(148, 163, 184, 0.12);
            }
            .mini-stat h4 {
                margin: 0;
                color: #64748b;
                font-size: 0.9rem;
                font-weight: 600;
            }
            .mini-stat p {
                margin: 0.4rem 0 0;
                font-size: 1.45rem;
                font-weight: 700;
                color: #0f172a;
            }
            .branch-card {
                background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.92));
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 20px;
                padding: 1rem;
                min-height: 210px;
            }
            .branch-card h4 {
                margin: 0 0 0.45rem;
                color: #111827;
            }
            .branch-card p {
                margin: 0.2rem 0;
                color: #475569;
            }
            .step-card {
                background: rgba(255, 255, 255, 0.9);
                border: 1px dashed rgba(99, 102, 241, 0.3);
                border-radius: 18px;
                padding: 0.95rem 1rem;
                min-height: 122px;
            }
            .step-card h4 {
                margin: 0 0 0.35rem;
                color: #312e81;
            }
            .step-card p {
                margin: 0;
                color: #475569;
                line-height: 1.7;
            }
            div[data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(148, 163, 184, 0.18);
                padding: 0.85rem;
                border-radius: 18px;
                box-shadow: 0 10px 24px rgba(148, 163, 184, 0.12);
            }
            div[data-testid="stForm"], div[data-testid="stExpander"], div[data-baseweb="select"] > div {
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.9);
            }
            div[data-testid="stDataFrame"], div[data-testid="stTabs"] {
                background: transparent;
            }
            .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
                border-radius: 14px;
                border: none;
                padding: 0.55rem 1rem;
                background: linear-gradient(135deg, #4f46e5, #ec4899);
                color: white;
                font-weight: 600;
            }
            .subtle-badge {
                display: inline-block;
                padding: 0.3rem 0.7rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.12);
                color: #e0e7ff;
                font-size: 0.85rem;
                margin-bottom: 0.7rem;
            }
            .quick-info {
                color: #334155;
                line-height: 1.8;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_banner(title: str, subtitle: str, badge: str) -> None:
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="subtle-badge">{badge}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(items: list[tuple[str, str]]) -> None:
    columns = st.columns(len(items))
    for col, (label, value) in zip(columns, items):
        with col:
            st.markdown(
                f'<div class="mini-stat"><h4>{label}</h4><p>{value}</p></div>',
                unsafe_allow_html=True,
            )


def render_hero(branch_count: int, total_services: int, total_bookings: int) -> None:
    render_page_banner(
        "منصة حجز صالونات سهلة وواضحة",
        "واجهة عربية عملية تنقل العميل من اختيار الفرع والخدمة إلى تأكيد الحجز ومتابعة دوره بدون تعقيد.",
        "تجربة استخدام جديدة",
    )
    render_stat_cards(
        [
            ("عدد الفروع", str(branch_count)),
            ("الخدمات المتاحة", str(total_services)),
            ("حجوزات اليوم", str(total_bookings)),
        ]
    )


def render_home() -> None:
    today_str = dt.date.today().isoformat()
    branches = get_branches()
    services = fetch_all("SELECT * FROM services")
    summary = get_dashboard_summary(today_str)

    render_hero(len(branches), len(services), summary["total_bookings"])
    st.write("")

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown(
            """
            <div class="soft-card">
                <div class="section-title">كيف يعمل النظام؟</div>
                <div class="quick-info">
                    1. يختار العميل الفرع والخدمة المناسبة له.<br>
                    2. يرى فقط المواعيد المتاحة فعلًا حسب الموظفين والطاقة التشغيلية.<br>
                    3. يحصل مباشرة على كود الحجز ورقم الدور واسم الموظف المخصص له.<br><br>
                    الواجهة الجديدة تركز على السرعة والوضوح وتقليل الخطوات غير المهمة.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        render_stat_cards(
            [
                ("العملاء بانتظار الخدمة", str(summary["waiting_count"])),
                ("الإيراد التقديري اليوم", f"{summary['estimated_revenue']:.0f} EGP"),
            ]
        )

    st.write("")
    st.markdown('<div class="section-title">ابدأ في 3 خطوات</div>', unsafe_allow_html=True)
    step_cols = st.columns(3)
    steps = [
        ("1. اختر الفرع", "كل فرع يعرض خدماته ومواعيد التشغيل الخاصة به بشكل مستقل."),
        ("2. حدد الخدمة", "يتم عرض السعر والمدة تلقائيًا لمساعدة العميل على القرار بسرعة."),
        ("3. أكد الموعد", "النظام يولد رقم الدور ويخصص موظفًا متاحًا تلقائيًا."),
    ]
    for col, (title, text) in zip(step_cols, steps):
        with col:
            st.markdown(
                f"""
                <div class="step-card">
                    <h4>{title}</h4>
                    <p>{text}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown('<div class="section-title">الفروع المتاحة</div>', unsafe_allow_html=True)
    branch_cols = st.columns(len(branches))
    for col, branch in zip(branch_cols, branches):
        branch_services = get_services(branch["id"])
        with col:
            st.markdown(
                f"""
                <div class="branch-card">
                    <h4>{branch["name"]}</h4>
                    <p>النوع: {branch["category"]}</p>
                    <p>الموقع: {branch["location"]}</p>
                    <p>ساعات العمل: {branch["open_hour"]}:00 - {branch["close_hour"]}:00</p>
                    <p>عدد الخدمات: {len(branch_services)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_booking_page() -> None:
    render_page_banner(
        "حجز سريع وواضح",
        "قسم الحجز مصمم بحيث يرى العميل الفرع والخدمة والموعد الملائم قبل إدخال بياناته، مع ملخص واضح للحجز في نفس الصفحة.",
        "تجربة الحجز",
    )
    branches = get_branches()
    branch_options = {f"{row['name']} - {row['location']}": row for row in branches}
    top_left, top_mid, top_right = st.columns([1.1, 1.2, 1])
    with top_left:
        branch_label = st.selectbox("الفرع", list(branch_options))
    selected_branch = branch_options[branch_label]

    services = get_services(selected_branch["id"])
    service_options = {
        f"{service['name']} | {service['duration_minutes']} دقيقة | {service['price']:.0f} EGP": service
        for service in services
    }
    with top_mid:
        service_label = st.selectbox("الخدمة", list(service_options))
    selected_service = service_options[service_label]
    with top_right:
        selected_date = st.date_input("التاريخ", min_value=dt.date.today())
    date_str = selected_date.isoformat()
    slots = build_available_slots(
        selected_branch["id"],
        selected_service["id"],
        date_str,
        selected_service["duration_minutes"],
    )
    staff_candidates = get_staff_for_service(selected_branch["id"], selected_service["id"])

    render_stat_cards(
        [
            ("السعر", f"{selected_service['price']:.0f} EGP"),
            ("مدة الخدمة", f"{selected_service['duration_minutes']} دقيقة"),
            ("المواعيد المتاحة", str(len(slots))),
            ("الموظفون للخدمة", str(len(staff_candidates))),
        ]
    )

    info_col, form_col = st.columns([0.95, 1.35])
    with info_col:
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="section-title">ملخص الاختيار</div>
                <div class="quick-info">
                    الفرع: <strong>{selected_branch["name"]}</strong><br>
                    الموقع: <strong>{selected_branch["location"]}</strong><br>
                    الخدمة: <strong>{selected_service["name"]}</strong><br>
                    مدة الخدمة: <strong>{selected_service["duration_minutes"]} دقيقة</strong><br>
                    السعر: <strong>{selected_service["price"]:.0f} EGP</strong><br>
                    التاريخ: <strong>{date_str}</strong><br><br>
                    يتم تخصيص الموظف تلقائيًا حسب أول شخص متاح للخدمة في الوقت المختار.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(
            """
            <div class="soft-card">
                <div class="section-title">نصيحة لتجربة أفضل</div>
                <div class="quick-info">
                    اختر الموعد الأقرب إذا كان هدفك سرعة الإنجاز، أو اختر تاريخًا لاحقًا إذا أردت مرونة أكبر في الأوقات المتاحة.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with form_col:
        with st.form("professional_booking_form"):
            st.markdown('<div class="section-title">بيانات العميل</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                client_name = st.text_input("الاسم الكامل")
            with col2:
                client_phone = st.text_input("رقم الهاتف")

            if slots:
                booking_time = st.selectbox("اختر الموعد المتاح", slots)
            else:
                booking_time = None
                st.warning("لا توجد مواعيد متاحة لهذا اليوم مع هذه الخدمة.")

            notes = st.text_area("ملاحظات إضافية", placeholder="مثال: يفضل موظف هادئ أو خدمة سريعة")
            submitted = st.form_submit_button("تأكيد الحجز الآن")

            if submitted:
                if not client_name.strip() or not client_phone.strip():
                    st.error("يرجى إدخال الاسم ورقم الهاتف بشكل صحيح.")
                elif booking_time is None:
                    st.error("اختر يومًا آخر أو خدمة أخرى لوجود ازدحام كامل.")
                else:
                    success, message, details = create_booking(
                        client_name,
                        client_phone,
                        selected_branch["id"],
                        selected_service["id"],
                        date_str,
                        booking_time,
                        notes,
                    )
                    if success:
                        st.success(message)
                        st.markdown(
                            f"""
                            <div class="ticket-card">
                                <div class="section-title">تم تأكيد الحجز</div>
                                <div class="quick-info">
                                    كود الحجز: <strong>{details['booking_code']}</strong><br>
                                    رقم الدور: <strong>#{details['queue_number']}</strong><br>
                                    الفرع: <strong>{details['branch_name']}</strong><br>
                                    الخدمة: <strong>{details['service_name']}</strong><br>
                                    الموظف المخصص: <strong>{details['staff_name']}</strong><br>
                                    الموعد: <strong>{details['date']} - {details['time']}</strong><br>
                                    السعر: <strong>{details['price']:.0f} EGP</strong>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.balloons()
                    else:
                        st.error(message)


def render_lookup_page() -> None:
    render_page_banner(
        "استعلام سريع عن حجوزات العميل",
        "أدخل رقم الهاتف للوصول إلى كل الحجوزات السابقة والقادمة في عرض بسيط ومباشر.",
        "متابعة العميل",
    )
    phone = st.text_input("رقم الهاتف المستخدم في الحجز")
    if st.button("بحث عن الحجوزات"):
        rows = get_customer_bookings(phone.strip())
        if not rows:
            st.warning("لا توجد حجوزات مرتبطة بهذا الرقم.")
            return

        st.markdown(
            f"""
            <div class="soft-card">
                <div class="section-title">نتيجة البحث</div>
                <div class="quick-info">تم العثور على <strong>{len(rows)}</strong> حجز مرتبط بهذا الرقم.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        for row in rows:
            st.markdown(
                f"""
                <div class="soft-card">
                    <div class="section-title">{row['service_name']}</div>
                    <div class="quick-info">
                        الفرع: <strong>{row['branch_name']}</strong><br>
                        كود الحجز: <strong>{row['booking_code']}</strong><br>
                        الموعد: <strong>{row['booking_date']} - {row['booking_time']}</strong><br>
                        الموظف: <strong>{row['staff_name']}</strong><br>
                        رقم الدور: <strong>#{row['queue_number']}</strong><br>
                        الحالة: <strong>{row['status']}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_queue_page() -> None:
    render_page_banner(
        "الطابور المباشر",
        "تابع رقم الدور الحالي في كل فرع وشاهد أقرب العملاء في قائمة الانتظار بشكل واضح وسريع.",
        "متابعة لحظية",
    )
    branches = get_branches()
    branch_options = {row["name"]: row for row in branches}
    col1, col2 = st.columns([1.2, 1])
    with col1:
        selected_branch_name = st.selectbox("اختر الفرع", list(branch_options))
    branch = branch_options[selected_branch_name]

    with col2:
        selected_date = st.date_input("تاريخ المتابعة", value=dt.date.today())
    date_str = selected_date.isoformat()
    current_serving = get_queue_status(branch["id"], date_str)
    bookings = get_bookings_with_details(branch["id"], date_str)
    waiting = [row for row in bookings if row["queue_number"] >= current_serving]

    render_stat_cards(
        [
            ("الدور الحالي", f"#{current_serving}"),
            ("إجمالي الحجوزات", str(len(bookings))),
            ("المتبقي في الانتظار", str(len(waiting))),
        ]
    )

    if waiting:
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="section-title">معلومة سريعة</div>
                <div class="quick-info">
                    الفرع الحالي: <strong>{branch["name"]}</strong><br>
                    أول عميل في الانتظار يحمل رقم <strong>#{waiting[0]['queue_number']}</strong>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown('<div class="section-title">العملاء القادمون</div>', unsafe_allow_html=True)
        preview = [
            {
                "رقم الدور": f"#{row['queue_number']}",
                "العميل": row["customer_name"],
                "الخدمة": row["service_name"],
                "الوقت": row["booking_time"],
                "الموظف": row["staff_name"],
            }
            for row in waiting[:8]
        ]
        st.dataframe(preview, use_container_width=True, hide_index=True)
    else:
        st.info("لا يوجد عملاء في قائمة الانتظار لهذا اليوم.")


def render_admin_page() -> None:
    render_page_banner(
        "لوحة إدارة التشغيل",
        "واجهة إدارية أبسط لمتابعة الحجوزات اليومية وتحديث رقم الدور وتحميل التقرير بسرعة.",
        "إدارة الفرع",
    )
    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    if not st.session_state.admin_ok:
        st.markdown(
            """
            <div class="soft-card">
                <div class="section-title">تسجيل دخول الإدارة</div>
                <div class="quick-info">أدخل كود الإدارة للوصول إلى أدوات التحكم الخاصة بالفروع.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        pin = st.text_input("كود الإدارة", type="password")
        access_col, note_col = st.columns([1, 1.4])
        with access_col:
            if st.button("دخول لوحة الإدارة"):
                if pin == ADMIN_PIN:
                    st.session_state.admin_ok = True
                    st.success("تم فتح لوحة الإدارة.")
                else:
                    st.error("الكود غير صحيح.")
        with note_col:
            st.info("الكود الافتراضي للتجربة: 1234")
        return

    branches = get_branches()
    branch_options = {row["name"]: row for row in branches}
    top1, top2, top3 = st.columns([1.2, 1, 0.8])
    with top1:
        selected_branch_name = st.selectbox("اختر الفرع", list(branch_options), key="admin_branch")
    branch = branch_options[selected_branch_name]
    with top2:
        selected_date = st.date_input("تاريخ التشغيل", value=dt.date.today(), key="admin_date")
    date_str = selected_date.isoformat()
    with top3:
        if st.button("تسجيل الخروج"):
            st.session_state.admin_ok = False
            st.rerun()

    bookings = get_bookings_with_details(branch["id"], date_str)
    current_serving = get_queue_status(branch["id"], date_str)
    estimated_revenue = sum(row["service_price"] for row in bookings)

    render_stat_cards(
        [
            ("حجوزات الفرع", str(len(bookings))),
            ("الدور الحالي", f"#{current_serving}"),
            ("الإيراد التقديري", f"{estimated_revenue:.0f} EGP"),
        ]
    )

    tab_summary, tab_queue, tab_bookings = st.tabs(
        ["ملخص التشغيل", "إدارة الطابور", "حجوزات اليوم"]
    )

    with tab_summary:
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="section-title">ملخص الفرع</div>
                <div class="quick-info">
                    الفرع: <strong>{branch["name"]}</strong><br>
                    الموقع: <strong>{branch["location"]}</strong><br>
                    النوع: <strong>{branch["category"]}</strong><br>
                    ساعات العمل: <strong>{branch["open_hour"]}:00 - {branch["close_hour"]}:00</strong><br>
                    تاريخ التشغيل: <strong>{date_str}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if bookings:
            next_customer = next(
                (row for row in bookings if row["queue_number"] >= current_serving),
                bookings[0],
            )
            st.markdown(
                f"""
                <div class="ticket-card">
                    <div class="section-title">أقرب عميل للتجهيز</div>
                    <div class="quick-info">
                        العميل: <strong>{next_customer["customer_name"]}</strong><br>
                        الخدمة: <strong>{next_customer["service_name"]}</strong><br>
                        الوقت: <strong>{next_customer["booking_time"]}</strong><br>
                        رقم الدور: <strong>#{next_customer["queue_number"]}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("لا توجد حجوزات حتى الآن لهذا التاريخ.")

    with tab_queue:
        st.markdown(
            """
            <div class="soft-card">
                <div class="section-title">تحديث رقم الدور</div>
                <div class="quick-info">حدّث الرقم الحالي بمجرد انتقال الخدمة للعميل التالي.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        next_turn = st.number_input(
            "رقم الدور الذي يتم خدمته الآن",
            min_value=1,
            max_value=max(len(bookings) + 5, 10),
            value=max(current_serving, 1),
        )
        if st.button("حفظ تحديث الدور"):
            set_queue_status(branch["id"], date_str, int(next_turn))
            st.success(f"تم تحديث الدور الحالي إلى #{int(next_turn)}.")

    with tab_bookings:
        if bookings:
            table = [
                {
                    "رقم الدور": row["queue_number"],
                    "كود الحجز": row["booking_code"],
                    "العميل": row["customer_name"],
                    "الهاتف": row["customer_phone"],
                    "الخدمة": row["service_name"],
                    "الموظف": row["staff_name"],
                    "الوقت": row["booking_time"],
                    "الحالة": row["status"],
                }
                for row in bookings
            ]
            st.dataframe(table, use_container_width=True, hide_index=True)
            st.download_button(
                "تحميل تقرير CSV",
                data=to_csv(bookings),
                file_name=f"bookings_{branch['id']}_{date_str}.csv",
                mime="text/csv",
            )
        else:
            st.info("لا توجد حجوزات لهذا الفرع في التاريخ المحدد.")


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="✂️", layout="wide")
    init_db()
    seed_demo_data()
    inject_style()

    st.title("✂️ منصة Glow & Groom")
    st.caption("نظام حجز صالونات عربي بتجربة أوضح، وتنقل أسهل، ولوحة تشغيل أبسط.")

    with st.sidebar:
        st.header("القائمة الرئيسية")
        page = st.radio(
            "انتقل إلى",
            [
                "الرئيسية",
                "احجز الآن",
                "استعلام العميل",
                "الطابور المباشر",
                "لوحة الإدارة",
            ],
        )
        st.markdown("---")
        st.markdown(
            """
            **ماذا يقدم النظام؟**

            - حجز سريع بخطوات قليلة
            - عرض مواعيد متاحة فعلية
            - متابعة الدور الحالي
            - لوحة إدارة سهلة
            """
        )
        st.info("يتم حفظ البيانات محليًا داخل SQLite، ويمكن تطوير التطبيق لاحقًا ليدعم تعدد المستخدمين والفروع.")

    if page == "الرئيسية":
        render_home()
    elif page == "احجز الآن":
        render_booking_page()
    elif page == "استعلام العميل":
        render_lookup_page()
    elif page == "الطابور المباشر":
        render_queue_page()
    else:
        render_admin_page()


if __name__ == "__main__":
    main()
