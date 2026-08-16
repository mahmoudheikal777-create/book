import csv
import datetime as dt
import io
import sqlite3
from pathlib import Path

import streamlit as st


APP_TITLE = "Glow & Groom Booking Hub"
DB_PATH = Path(__file__).with_name("salon_booking.db")
ADMIN_PIN = "1234"


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
            """
        )


def seed_demo_data() -> None:
    with connect_db() as conn:
        branch_count = conn.execute("SELECT COUNT(*) FROM branches").fetchone()[0]
        if branch_count:
            return

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
        WHERE customers.phone = ?
        ORDER BY bookings.booking_date DESC, bookings.booking_time DESC
        """,
        (phone,),
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
    with connect_db() as conn:
        customer = conn.execute(
            "SELECT id FROM customers WHERE phone = ?",
            (phone,),
        ).fetchone()
        if customer:
            conn.execute(
                "UPDATE customers SET full_name = ? WHERE id = ?",
                (name, customer["id"]),
            )
            return customer["id"]

        cursor = conn.execute(
            "INSERT INTO customers (full_name, phone) VALUES (?, ?)",
            (name, phone),
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
    service = fetch_one(
        "SELECT name, duration_minutes, price FROM services WHERE id = ?",
        (service_id,),
    )
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
    customer_id = upsert_customer(name.strip(), phone.strip())

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

    branch = fetch_one("SELECT name FROM branches WHERE id = ?", (branch_id,))
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
                background:
                    radial-gradient(circle at top left, rgba(255,255,255,0.18), transparent 28%),
                    linear-gradient(135deg, #0f172a 0%, #111827 42%, #1f2937 100%);
                color: #f8fafc;
            }
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1150px;
            }
            .hero-card, .glass-card {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 22px;
                padding: 1.2rem 1.4rem;
                backdrop-filter: blur(10px);
                box-shadow: 0 14px 35px rgba(15, 23, 42, 0.22);
            }
            .hero-title {
                font-size: 2.3rem;
                font-weight: 700;
                margin-bottom: 0.45rem;
            }
            .hero-subtitle {
                color: #dbe4ff;
                line-height: 1.7;
                margin-bottom: 0;
            }
            .mini-stat {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 18px;
                padding: 0.9rem 1rem;
                text-align: center;
            }
            .mini-stat h4 {
                margin: 0;
                color: #93c5fd;
                font-size: 0.95rem;
            }
            .mini-stat p {
                margin: 0.35rem 0 0;
                font-size: 1.35rem;
                font-weight: 700;
                color: #ffffff;
            }
            div[data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 0.8rem;
                border-radius: 18px;
            }
            div[data-testid="stForm"], div[data-testid="stExpander"] {
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.06);
            }
            .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
                border-radius: 14px;
                border: none;
                background: linear-gradient(135deg, #8b5cf6, #ec4899);
                color: white;
                font-weight: 600;
            }
            .section-label {
                font-size: 1.15rem;
                font-weight: 700;
                margin: 0.25rem 0 0.7rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(branch_count: int, total_services: int, total_bookings: int) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">صالونات وحجوزات بشكل احترافي</div>
            <p class="hero-subtitle">
                منصة موحدة لإدارة الحجز والطوابير والخدمات والموظفين في واجهة أنيقة وسريعة.
                صممت لتناسب صالونات الحلاقة والتجميل مع قابلية التوسع لأي فرع جديد.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="mini-stat"><h4>الفروع</h4><p>{branch_count}</p></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="mini-stat"><h4>الخدمات</h4><p>{total_services}</p></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="mini-stat"><h4>حجوزات اليوم</h4><p>{total_bookings}</p></div>',
            unsafe_allow_html=True,
        )


def render_home() -> None:
    today_str = dt.date.today().isoformat()
    branches = get_branches()
    services = fetch_all("SELECT * FROM services")
    summary = get_dashboard_summary(today_str)

    render_hero(len(branches), len(services), summary["total_bookings"])
    st.write("")

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">لماذا هذه النسخة أقوى؟</div>', unsafe_allow_html=True)
        st.write(
            """
            - حفظ دائم للحجوزات والطابور داخل قاعدة بيانات `SQLite`.
            - توزيع ذكي للعميل على أول موظف متاح حسب الخدمة والموعد.
            - لوحة متابعة مباشرة للفروع مع تحديث رقم الدور الحالي.
            - تصميم أنظف يصلح كنقطة انطلاق لتطبيق تجاري فعلي.
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">مؤشرات اليوم</div>', unsafe_allow_html=True)
        st.metric("إجمالي الحجوزات", summary["total_bookings"])
        st.metric("العملاء قيد الانتظار", summary["waiting_count"])
        st.metric("الإيراد التقديري", f"{summary['estimated_revenue']:.0f} EGP")
        st.markdown("</div>", unsafe_allow_html=True)


def render_booking_page() -> None:
    branches = get_branches()
    branch_options = {f"{row['name']} - {row['location']}": row for row in branches}
    branch_label = st.selectbox("اختر الفرع", list(branch_options))
    selected_branch = branch_options[branch_label]

    services = get_services(selected_branch["id"])
    service_options = {
        f"{service['name']} | {service['duration_minutes']} دقيقة | {service['price']:.0f} EGP": service
        for service in services
    }
    service_label = st.selectbox("اختر الخدمة", list(service_options))
    selected_service = service_options[service_label]

    selected_date = st.date_input("تاريخ الحجز", min_value=dt.date.today())
    date_str = selected_date.isoformat()
    slots = build_available_slots(
        selected_branch["id"],
        selected_service["id"],
        date_str,
        selected_service["duration_minutes"],
    )

    with st.form("professional_booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("اسم العميل")
        with col2:
            client_phone = st.text_input("رقم الهاتف")

        if slots:
            booking_time = st.selectbox("المواعيد المتاحة", slots)
        else:
            booking_time = None
            st.warning("لا توجد مواعيد متاحة لهذا اليوم مع هذه الخدمة.")

        notes = st.text_area("ملاحظات إضافية", placeholder="اختياري: تفضيلات أو طلبات خاصة")
        submitted = st.form_submit_button("تأكيد الحجز")

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
                        <div class="glass-card">
                            <div class="section-label">تفاصيل الحجز</div>
                            <p>كود الحجز: <strong>{details['booking_code']}</strong></p>
                            <p>رقم الدور: <strong>#{details['queue_number']}</strong></p>
                            <p>الفرع: <strong>{details['branch_name']}</strong></p>
                            <p>الخدمة: <strong>{details['service_name']}</strong></p>
                            <p>الموظف المخصص: <strong>{details['staff_name']}</strong></p>
                            <p>الموعد: <strong>{details['date']} - {details['time']}</strong></p>
                            <p>السعر: <strong>{details['price']:.0f} EGP</strong></p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.balloons()
                else:
                    st.error(message)


def render_lookup_page() -> None:
    st.markdown('<div class="section-label">استعلام عن حجوزات العميل</div>', unsafe_allow_html=True)
    phone = st.text_input("أدخل رقم الهاتف المستخدم في الحجز")
    if st.button("بحث عن الحجوزات"):
        rows = get_customer_bookings(phone.strip())
        if not rows:
            st.warning("لا توجد حجوزات مرتبطة بهذا الرقم.")
            return

        for row in rows:
            st.markdown(
                f"""
                <div class="glass-card">
                    <p><strong>{row['branch_name']}</strong> | {row['service_name']}</p>
                    <p>كود الحجز: <strong>{row['booking_code']}</strong></p>
                    <p>الموعد: <strong>{row['booking_date']} - {row['booking_time']}</strong></p>
                    <p>الموظف: <strong>{row['staff_name']}</strong> | رقم الدور: <strong>#{row['queue_number']}</strong></p>
                    <p>الحالة: <strong>{row['status']}</strong></p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_queue_page() -> None:
    branches = get_branches()
    branch_options = {row["name"]: row for row in branches}
    selected_branch_name = st.selectbox("اختر الفرع لمتابعة الطابور", list(branch_options))
    branch = branch_options[selected_branch_name]

    selected_date = st.date_input("تاريخ المتابعة", value=dt.date.today())
    date_str = selected_date.isoformat()
    current_serving = get_queue_status(branch["id"], date_str)
    bookings = get_bookings_with_details(branch["id"], date_str)
    waiting = [row for row in bookings if row["queue_number"] >= current_serving]

    st.metric("الدور الحالي", f"#{current_serving}")
    st.metric("عدد الحجوزات اليوم", len(bookings))
    st.metric("المتبقي في الانتظار", len(waiting))

    if waiting:
        st.markdown('<div class="section-label">الطوابير القادمة</div>', unsafe_allow_html=True)
        preview = [
            {
                "Queue": f"#{row['queue_number']}",
                "Client": row["customer_name"],
                "Service": row["service_name"],
                "Time": row["booking_time"],
                "Staff": row["staff_name"],
            }
            for row in waiting[:8]
        ]
        st.dataframe(preview, use_container_width=True, hide_index=True)
    else:
        st.info("لا يوجد عملاء في قائمة الانتظار لهذا اليوم.")


def render_admin_page() -> None:
    st.markdown('<div class="section-label">لوحة إدارة الفرع</div>', unsafe_allow_html=True)
    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    if not st.session_state.admin_ok:
        pin = st.text_input("أدخل كود الإدارة", type="password")
        if st.button("دخول"):
            if pin == ADMIN_PIN:
                st.session_state.admin_ok = True
                st.success("تم فتح لوحة الإدارة.")
            else:
                st.error("الكود غير صحيح.")
        st.caption("الكود الافتراضي للتجربة: 1234")
        return

    branches = get_branches()
    branch_options = {row["name"]: row for row in branches}
    selected_branch_name = st.selectbox("الفرع", list(branch_options), key="admin_branch")
    branch = branch_options[selected_branch_name]
    selected_date = st.date_input("تاريخ التشغيل", value=dt.date.today(), key="admin_date")
    date_str = selected_date.isoformat()

    bookings = get_bookings_with_details(branch["id"], date_str)
    current_serving = get_queue_status(branch["id"], date_str)
    estimated_revenue = sum(row["service_price"] for row in bookings)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي حجوزات الفرع", len(bookings))
    with col2:
        st.metric("الدور الحالي", f"#{current_serving}")
    with col3:
        st.metric("إيراد تقديري", f"{estimated_revenue:.0f} EGP")

    with st.expander("تحديث الدور الحالي", expanded=True):
        next_turn = st.number_input(
            "رقم الدور الذي يتم خدمته الآن",
            min_value=1,
            max_value=max(len(bookings) + 5, 10),
            value=max(current_serving, 1),
        )
        if st.button("حفظ التحديث"):
            set_queue_status(branch["id"], date_str, int(next_turn))
            st.success(f"تم تحديث الدور الحالي إلى #{int(next_turn)}.")

    st.markdown('<div class="section-label">حجوزات اليوم</div>', unsafe_allow_html=True)
    if bookings:
        table = [
            {
                "Queue": row["queue_number"],
                "Code": row["booking_code"],
                "Client": row["customer_name"],
                "Phone": row["customer_phone"],
                "Service": row["service_name"],
                "Staff": row["staff_name"],
                "Time": row["booking_time"],
                "Status": row["status"],
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

    st.title("✂️ Glow & Groom Booking Hub")
    st.caption("Professional booking, queue tracking, and branch operations in one Streamlit app.")

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "اختر القسم",
            [
                "الرئيسية",
                "احجز الآن",
                "استعلام العميل",
                "الطابور المباشر",
                "لوحة الإدارة",
            ],
        )
        st.info("النظام يحفظ البيانات محليًا داخل SQLite ويمكن تطويره لاحقًا لتعدد الفروع والمستخدمين.")

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
