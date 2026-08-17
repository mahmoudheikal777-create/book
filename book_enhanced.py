"""
Glow & Groom Salon Booking System - Enhanced Version
Professional Arabic-Friendly Booking Platform
"""

import csv
import datetime as dt
import io
import sqlite3
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st

# ============ CONSTANTS ============
APP_TITLE = "Glow & Groom Booking Hub"
DB_PATH = Path(__file__).with_name("salon_booking.db")
ADMIN_PIN = "1234"

# ============ STYLING ============
def inject_professional_css() -> None:
    """Inject comprehensive professional CSS styling"""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Cairo:wght@300;400;600;700&display=swap');
            
            :root {
                --primary: #6366f1;
                --primary-light: #818cf8;
                --primary-dark: #4f46e5;
                --secondary: #ec4899;
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --gray-50: #f9fafb;
                --gray-100: #f3f4f6;
                --gray-200: #e5e7eb;
                --gray-300: #d1d5db;
                --gray-400: #9ca3af;
                --gray-500: #6b7280;
                --gray-600: #4b5563;
                --gray-700: #374151;
                --gray-800: #1f2937;
                --gray-900: #111827;
            }
            
            * {
                font-family: 'Cairo', 'Poppins', sans-serif;
            }
            
            html {
                direction: rtl;
                scroll-behavior: smooth;
            }
            
            .stApp {
                direction: rtl;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: var(--gray-800);
                overflow-x: hidden;
            }
            
            .block-container {
                max-width: 1400px;
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            
            /* SIDEBAR */
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, var(--gray-900) 0%, var(--gray-800) 100%);
                border-right: 1px solid rgba(255,255,255,0.1);
            }
            
            section[data-testid="stSidebar"] * {
                color: #f8fafc !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > label {
                color: #e2e8f0 !important;
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 8px;
                transition: all 0.3s ease;
                background: rgba(255,255,255,0.05);
            }
            
            section[data-testid="stSidebar"] .stRadio > label:hover {
                background: rgba(255,255,255,0.1);
                transform: translateX(4px);
            }
            
            section[data-testid="stSidebar"] .stRadio > label[data-state="checked"] {
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
            }
            
            /* PAGE HERO */
            .page-hero {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 24px;
                padding: 2.5rem 2rem;
                color: #ffffff;
                border: 1px solid rgba(255,255,255,0.2);
                box-shadow: 0 25px 50px rgba(0,0,0,0.15);
                margin-bottom: 2rem;
                animation: slideInDown 0.6s ease;
                position: relative;
                overflow: hidden;
            }
            
            .page-hero::before {
                content: '';
                position: absolute;
                top: -50%;
                right: -10%;
                width: 400px;
                height: 400px;
                background: rgba(255,255,255,0.1);
                border-radius: 50%;
                animation: float 6s ease-in-out infinite;
            }
            
            .page-hero::after {
                content: '';
                position: absolute;
                bottom: -30%;
                left: -10%;
                width: 300px;
                height: 300px;
                background: rgba(255,255,255,0.05);
                border-radius: 50%;
                animation: float 8s ease-in-out infinite reverse;
            }
            
            .page-hero > * {
                position: relative;
                z-index: 2;
            }
            
            .page-hero h1 {
                margin: 0;
                font-size: 2.5rem;
                font-weight: 700;
                line-height: 1.2;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .page-hero p {
                margin: 0.75rem 0 0;
                color: rgba(255,255,255,0.95);
                line-height: 1.8;
                font-size: 1.05rem;
                max-width: 90%;
            }
            
            .subtle-badge {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                background: rgba(255,255,255,0.2);
                color: #e0e7ff;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 1rem;
                border: 1px solid rgba(255,255,255,0.3);
                letter-spacing: 0.5px;
            }
            
            /* ANIMATIONS */
            @keyframes slideInDown {
                from {
                    opacity: 0;
                    transform: translateY(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-20px); }
            }
            
            /* STAT CARDS */
            .stat-card {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(99,102,241,0.1);
                border-radius: 16px;
                padding: 1.5rem 1.25rem;
                box-shadow: 0 10px 15px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                animation: slideInUp 0.6s ease;
                min-height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            
            .stat-card:hover {
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(99,102,241,0.15);
                border-color: rgba(99,102,241,0.3);
            }
            
            .stat-card h4 {
                margin: 0;
                color: var(--gray-600);
                font-size: 0.85rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .stat-card p {
                margin: 0.75rem 0 0;
                font-size: 1.75rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .stat-card .stat-icon {
                font-size: 1.8rem;
                margin-bottom: 0.5rem;
            }
            
            /* CARDS */
            .soft-card, .ticket-card {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(148,163,184,0.2);
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                transition: all 0.3s ease;
                animation: slideInUp 0.6s ease;
            }
            
            .soft-card:hover {
                border-color: rgba(99,102,241,0.3);
                box-shadow: 0 10px 15px rgba(0,0,0,0.1);
                transform: translateY(-4px);
            }
            
            .ticket-card {
                background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(236,72,153,0.1) 100%);
                border: 1px solid rgba(99,102,241,0.2);
                position: relative;
            }
            
            /* SECTION TITLES */
            .section-title {
                font-size: 1.25rem;
                font-weight: 700;
                margin: 0 0 1rem;
                color: var(--gray-900);
                position: relative;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }
            
            .section-title::before {
                content: '';
                width: 4px;
                height: 1.25rem;
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                border-radius: 2px;
            }
            
            .quick-info {
                color: var(--gray-600);
                line-height: 1.8;
                margin-bottom: 0;
                font-size: 0.95rem;
            }
            
            /* BRANCH CARDS */
            .branch-card {
                background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.96) 100%);
                border: 1px solid rgba(148,163,184,0.2);
                border-radius: 16px;
                padding: 1.5rem;
                min-height: 240px;
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                animation: slideInUp 0.6s ease;
                position: relative;
                overflow: hidden;
            }
            
            .branch-card:hover {
                transform: translateY(-6px);
                box-shadow: 0 15px 40px rgba(99,102,241,0.15);
                border-color: rgba(99,102,241,0.3);
            }
            
            .branch-card h4 {
                margin: 0 0 0.75rem;
                color: var(--gray-900);
                font-size: 1.1rem;
                font-weight: 700;
            }
            
            .branch-card p {
                margin: 0.4rem 0;
                color: var(--gray-600);
                font-size: 0.9rem;
            }
            
            .branch-card .badge {
                display: inline-block;
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-top: 0.5rem;
            }
            
            /* STEP CARDS */
            .step-card {
                background: rgba(255,255,255,0.9);
                border: 2px dashed rgba(99,102,241,0.3);
                border-radius: 16px;
                padding: 1.5rem;
                min-height: 150px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                transition: all 0.3s ease;
                animation: slideInUp 0.6s ease;
            }
            
            .step-card:hover {
                border-color: rgba(99,102,241,0.6);
                background: rgba(255,255,255,0.95);
                transform: translateY(-4px);
                box-shadow: 0 10px 25px rgba(99,102,241,0.1);
            }
            
            .step-card h4 {
                margin: 0 0 0.5rem;
                color: var(--primary-dark);
                font-size: 1rem;
                font-weight: 700;
            }
            
            .step-card p {
                margin: 0;
                color: var(--gray-600);
                line-height: 1.6;
                font-size: 0.9rem;
            }
            
            /* FORMS & BUTTONS */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea {
                border-radius: 12px !important;
                border: 1px solid var(--gray-300) !important;
                padding: 10px 12px !important;
                transition: all 0.3s ease !important;
            }
            
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {
                border-color: var(--primary) !important;
                box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
            }
            
            .stButton > button, 
            .stFormSubmitButton > button {
                border-radius: 12px !important;
                border: none !important;
                padding: 10px 20px !important;
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
                color: white !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 12px rgba(99,102,241,0.3) !important;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .stButton > button:hover, 
            .stFormSubmitButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 20px rgba(99,102,241,0.4) !important;
            }
            
            /* ALERTS */
            .stAlert {
                border-radius: 16px !important;
                border-left: 4px solid !important;
                padding: 1rem !important;
                animation: slideInUp 0.3s ease !important;
            }
            
            /* METRICS */
            div[data-testid="stMetric"] {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(148,163,184,0.2);
                padding: 1.25rem;
                border-radius: 16px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            }
            
            /* RESPONSIVE */
            @media (max-width: 768px) {
                .page-hero h1 {
                    font-size: 1.8rem;
                }
                .page-hero p {
                    font-size: 0.9rem;
                }
                .stat-card {
                    min-height: 120px;
                }
                .branch-card {
                    min-height: 200px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============ UTILITY FUNCTIONS ============
def normalize_phone(phone: str) -> str:
    """نرمال الأرقام الهاتفية"""
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    return digits if len(digits) >= 10 else (phone or "").strip()


def is_valid_phone(phone: str) -> bool:
    """التحقق من صحة رقم الهاتف"""
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    return 10 <= len(digits) <= 15


def get_language() -> str:
    """الحصول على اللغة الحالية"""
    return st.session_state.get("lang", "ar")


def text(ar: str, en: str) -> str:
    """عرض نص بناءً على اللغة المختارة"""
    return ar if get_language() == "ar" else en


def localized_value(ar_value: str | None, en_value: str | None) -> str:
    """قيمة محلية بناءً على اللغة"""
    if get_language() == "ar":
        return ar_value or en_value or ""
    return en_value or ar_value or ""


def image_url(prompt: str, image_size: str = "landscape_4_3") -> str:
    """توليد صورة من نص"""
    return (
        "https://coresg-normal.trae.ai/api/ide/v1/text_to_image"
        f"?prompt={quote(prompt)}&image_size={image_size}"
    )


# ============ DATABASE FUNCTIONS ============
def connect_db() -> sqlite3.Connection:
    """اتصال قاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """تهيئة قاعدة البيانات"""
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
                phone TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                branch_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                staff_id INTEGER NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                status TEXT DEFAULT 'confirmed',
                booking_code TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(customer_id) REFERENCES customers(id),
                FOREIGN KEY(branch_id) REFERENCES branches(id),
                FOREIGN KEY(service_id) REFERENCES services(id),
                FOREIGN KEY(staff_id) REFERENCES staff(id)
            );

            CREATE TABLE IF NOT EXISTS queue_status (
                branch_id INTEGER PRIMARY KEY,
                current_queue_number INTEGER DEFAULT 1,
                FOREIGN KEY(branch_id) REFERENCES branches(id)
            );

            CREATE INDEX IF NOT EXISTS idx_bookings_branch_date 
            ON bookings(branch_id, booking_date);
            CREATE INDEX IF NOT EXISTS idx_bookings_staff_date 
            ON bookings(staff_id, booking_date);
            CREATE INDEX IF NOT EXISTS idx_customers_phone 
            ON customers(phone);
        """
        )
        conn.commit()


def fetch_one(query: str, params: tuple = ()):
    """جلب سجل واحد"""
    with connect_db() as conn:
        return conn.execute(query, params).fetchone()


def fetch_all(query: str, params: tuple = ()):
    """جلب جميع السجلات"""
    with connect_db() as conn:
        return conn.execute(query, params).fetchall()


def execute_write(query: str, params: tuple = ()):
    """تنفيذ عملية كتابة"""
    with connect_db() as conn:
        conn.execute(query, params)
        conn.commit()


# ============ COMPONENT RENDERING ============
def render_page_banner(title: str, subtitle: str, badge: str, icon: str = "") -> None:
    """عرض بنر الصفحة"""
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="subtle-badge">{icon} {badge}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(items: list[tuple[str, str, str]]) -> None:
    """عرض بطاقات الإحصائيات"""
    cols = st.columns(len(items))
    for col, (label, value, icon) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-icon">{icon}</div>
                    <h4>{label}</h4>
                    <p>{value}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_soft_card(title: str, content: str, icon: str = "") -> None:
    """عرض بطاقة ناعمة"""
    st.markdown(
        f"""
        <div class="soft-card">
            <div style="display: flex; gap: 1rem; align-items: flex-start;">
                <div style="font-size: 1.5rem;">{icon}</div>
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 0.5rem; color: #1f2937;">{title}</h3>
                    <div style="color: #4b5563; line-height: 1.8;">
                        {content}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_branch_card(name: str, category: str, location: str, hours: str, services: int, icon: str) -> None:
    """عرض بطاقة الفرع"""
    st.markdown(
        f"""
        <div class="branch-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <h4>{name}</h4>
            <p><strong>الفئة:</strong> {category}</p>
            <p><strong>الموقع:</strong> {location}</p>
            <p><strong>الساعات:</strong> {hours}</p>
            <p><strong>الخدمات:</strong> {services}</p>
            <div class="badge">متاح الآن ✓</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_cards(steps: list[tuple[str, str, str]]) -> None:
    """عرض بطاقات الخطوات"""
    cols = st.columns(len(steps))
    for col, (title, desc, icon) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
                <div class="step-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_success_message(code: str, queue_number: int, staff_name: str, slot: str) -> None:
    """عرض رسالة النجاح"""
    st.markdown(
        f"""
        <div class="ticket-card" style="padding: 2rem;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 3rem;">✅</div>
                <h2 style="color: #10b981; margin: 0.5rem 0;">تم تأكيد حجزك بنجاح!</h2>
            </div>
            <div style="background: rgba(255,255,255,0.5); padding: 1.5rem; border-radius: 12px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <p style="color: #6b7280; font-size: 0.85rem; margin: 0;">كود الحجز</p>
                        <p style="color: #111827; font-size: 1.25rem; font-weight: 700; margin: 0.25rem 0;">{code}</p>
                    </div>
                    <div>
                        <p style="color: #6b7280; font-size: 0.85rem; margin: 0;">رقم الدور</p>
                        <p style="color: #111827; font-size: 1.25rem; font-weight: 700; margin: 0.25rem 0;">#{queue_number}</p>
                    </div>
                </div>
                <hr style="margin: 1rem 0; border: none; border-top: 1px solid rgba(0,0,0,0.1);">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <p style="color: #6b7280; font-size: 0.85rem; margin: 0;">الموظف المخصص</p>
                        <p style="color: #111827; font-size: 1rem; font-weight: 600; margin: 0.25rem 0;">{staff_name}</p>
                    </div>
                    <div>
                        <p style="color: #6b7280; font-size: 0.85rem; margin: 0;">الموعد</p>
                        <p style="color: #111827; font-size: 1rem; font-weight: 600; margin: 0.25rem 0;">{slot}</p>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============ DATABASE QUERIES ============
def get_branches() -> list:
    """الحصول على قائمة الفروع"""
    return fetch_all("SELECT * FROM branches")


def get_services(branch_id: int) -> list:
    """الحصول على خدمات الفرع"""
    return fetch_all("SELECT * FROM services WHERE branch_id = ?", (branch_id,))


def get_staff_for_service(branch_id: int, service_id: int) -> list:
    """الحصول على الموظفين للخدمة"""
    query = """
    SELECT DISTINCT s.* FROM staff s
    INNER JOIN staff_services ss ON s.id = ss.staff_id
    WHERE s.branch_id = ? AND ss.service_id = ?
    """
    return fetch_all(query, (branch_id, service_id))


def get_customer_bookings(phone: str) -> list:
    """الحصول على حجوزات العميل"""
    query = """
    SELECT b.*, c.name, br.name as branch_name, s.name as service_name, st.name as staff_name
    FROM bookings b
    INNER JOIN customers c ON b.customer_id = c.id
    INNER JOIN branches br ON b.branch_id = br.id
    INNER JOIN services s ON b.service_id = s.id
    INNER JOIN staff st ON b.staff_id = st.id
    WHERE c.phone = ?
    ORDER BY b.booking_date DESC, b.booking_time DESC
    """
    return fetch_all(query, (normalize_phone(phone),))


def get_dashboard_summary(date_str: str) -> dict:
    """الحصول على ملخص لوحة التحكم"""
    today_bookings = fetch_all(
        "SELECT COUNT(*) as count FROM bookings WHERE booking_date = ?", (date_str,)
    )[0]["count"]
    
    total_revenue = fetch_all(
        """
        SELECT SUM(s.price) as total FROM bookings b
        INNER JOIN services s ON b.service_id = s.id
        WHERE b.booking_date = ?
        """,
        (date_str,),
    )[0]["total"] or 0
    
    waiting = fetch_all(
        "SELECT COUNT(*) as count FROM bookings WHERE booking_date = ? AND status = 'waiting'",
        (date_str,),
    )[0]["count"]
    
    return {
        "total_bookings": today_bookings,
        "estimated_revenue": total_revenue,
        "waiting_count": waiting,
    }


# ============ PAGE RENDERERS ============
def render_home() -> None:
    """الصفحة الرئيسية"""
    today_str = dt.date.today().isoformat()
    branches = get_branches()
    services = fetch_all("SELECT * FROM services")
    summary = get_dashboard_summary(today_str)

    render_page_banner(
        "منصة حجز صالونات",
        "واجهة عربية محترفة تنقل العميل من الاختيار إلى تأكيد الحجز ومتابعة الدور بدون تعقيد.",
        "تجربة حجز جديدة",
        "✂️"
    )
    
    render_stat_cards([
        ("عدد الفروع", str(len(branches)), "🏢"),
        ("الخدمات المتاحة", str(len(services)), "💼"),
        ("حجوزات اليوم", str(summary["total_bookings"]), "📅"),
    ])

    st.write("")
    left, right = st.columns([1.2, 1])
    
    with left:
        render_soft_card(
            "كيف يعمل النظام؟",
            "<strong>1.</strong> اختيار الفرع والخدمة<br>"
            "<strong>2.</strong> اختيار الموعد المناسب<br>"
            "<strong>3.</strong> تأكيد الحجز والحصول على الكود<br>"
            "<em style='color: #667eea;'>واجهة سريعة وسهلة وواضحة!</em>",
            "⚙️"
        )
    
    with right:
        render_stat_cards([
            ("بانتظار الخدمة", str(summary["waiting_count"]), "⏳"),
            ("الإيراد اليوم", f"EGP {summary['estimated_revenue']:.0f}", "💰"),
        ])

    st.write("")
    st.markdown('<div class="section-title">ابدأ في 3 خطوات سهلة</div>', unsafe_allow_html=True)
    
    render_step_cards([
        ("اختر الفرع", "كل فرع يعرض خدماته ومواعيد التشغيل", "🏪"),
        ("حدد الخدمة", "السعر والمدة تظهر تلقائيًا", "💇"),
        ("أكد الموعد", "النظام يخصص موظفًا متاحًا", "✅"),
    ])

    st.write("")
    st.markdown('<div class="section-title">الفروع المتاحة</div>', unsafe_allow_html=True)
    
    branch_cols = st.columns(min(len(branches), 3))
    for col, branch in zip(branch_cols, branches):
        branch_services = get_services(branch["id"])
        with col:
            icon = "💆" if "Beauty" in branch["category"] else "💈" if "Barber" in branch["category"] else "🏢"
            render_branch_card(
                branch["name"],
                branch["category"],
                branch["location"],
                f"{branch['open_hour']}:00 - {branch['close_hour']}:00",
                len(branch_services),
                icon
            )


def render_booking_page() -> None:
    """صفحة الحجز"""
    render_page_banner(
        "احجز موعدك الآن",
        "اختر الفرع والخدمة والموعد المناسب لك",
        "حجز جديد",
        "📅"
    )
    
    branches = get_branches()
    if not branches:
        st.error("لا توجد فروع متاحة")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        branch_names = [b["name"] for b in branches]
        selected_branch_name = st.selectbox("اختر الفرع:", branch_names)
        branch = next(b for b in branches if b["name"] == selected_branch_name)
    
    with col2:
        services = get_services(branch["id"])
        if services:
            service_names = [s["name"] for s in services]
            selected_service_name = st.selectbox("اختر الخدمة:", service_names)
            service = next(s for s in services if s["name"] == selected_service_name)
        else:
            st.error("لا توجد خدمات متاحة لهذا الفرع")
            return
    
    st.write("")
    
    # عرض تفاصيل الخدمة
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="soft-card">
                <h4 style="margin: 0;">تفاصيل الخدمة</h4>
                <p><strong>المدة:</strong> {service['duration_minutes']} دقيقة</p>
                <p><strong>السعر:</strong> {service['price']} جنيه</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # اختيار التاريخ والوقت
    with col2:
        booking_date = st.date_input("اختر التاريخ:")
        booking_time = st.time_input("اختر الوقت:")
    
    st.write("")
    
    # بيانات العميل
    st.markdown('<div class="section-title">بيانات التواصل</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("اسمك:")
    
    with col2:
        customer_phone = st.text_input("رقم هاتفك:")
    
    st.write("")
    
    if st.button("تأكيد الحجز", use_container_width=True):
        # التحقق من البيانات
        if not customer_name or len(customer_name) < 2:
            st.error("الرجاء إدخال اسم صحيح")
            return
        
        if not is_valid_phone(customer_phone):
            st.error("الرجاء إدخال رقم هاتف صحيح (10-15 أرقام)")
            return
        
        # إضافة العميل
        normalized_phone = normalize_phone(customer_phone)
        customer = fetch_one(
            "SELECT id FROM customers WHERE phone = ?", (normalized_phone,)
        )
        
        if customer:
            customer_id = customer["id"]
        else:
            execute_write(
                "INSERT INTO customers (name, phone) VALUES (?, ?)",
                (customer_name, normalized_phone),
            )
            customer_id = fetch_one(
                "SELECT id FROM customers WHERE phone = ?", (normalized_phone,)
            )["id"]
        
        # الحصول على الموظفين المتاحين
        available_staff = get_staff_for_service(branch["id"], service["id"])
        if not available_staff:
            st.error("لا يوجد موظفون متاحون لهذه الخدمة")
            return
        
        staff = available_staff[0]
        
        # إنشاء رمز الحجز
        booking_code = f"BK{dt.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # حفظ الحجز
        execute_write(
            """
            INSERT INTO bookings 
            (customer_id, branch_id, service_id, staff_id, booking_date, booking_time, booking_code, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'confirmed')
            """,
            (customer_id, branch["id"], service["id"], staff["id"], 
             booking_date.isoformat(), booking_time.isoformat(), booking_code),
        )
        
        # الحصول على رقم الدور
        queue_status = fetch_one(
            "SELECT current_queue_number FROM queue_status WHERE branch_id = ?",
            (branch["id"],),
        )
        
        if queue_status:
            queue_number = queue_status["current_queue_number"]
            execute_write(
                "UPDATE queue_status SET current_queue_number = current_queue_number + 1 WHERE branch_id = ?",
                (branch["id"],),
            )
        else:
            queue_number = 1
            execute_write(
                "INSERT INTO queue_status (branch_id, current_queue_number) VALUES (?, 2)",
                (branch["id"],),
            )
        
        # عرض رسالة النجاح
        render_success_message(
            booking_code,
            queue_number,
            staff["name"],
            f"{booking_date} {booking_time}"
        )
        
        st.balloons()


def render_lookup_page() -> None:
    """صفحة البحث عن الحجوزات"""
    render_page_banner(
        "ابحث عن حجزك",
        "أدخل رقم هاتفك للاطلاع على حجوزاتك",
        "البحث",
        "🔍"
    )
    
    phone = st.text_input("رقم الهاتف:")
    
    if phone and is_valid_phone(phone):
        bookings = get_customer_bookings(phone)
        
        if bookings:
            st.markdown('<div class="section-title">حجوزاتك</div>', unsafe_allow_html=True)
            
            for booking in bookings:
                st.markdown(
                    f"""
                    <div class="ticket-card">
                        <p><strong>الفرع:</strong> {booking['branch_name']}</p>
                        <p><strong>الخدمة:</strong> {booking['service_name']}</p>
                        <p><strong>الموظف:</strong> {booking['staff_name']}</p>
                        <p><strong>التاريخ والوقت:</strong> {booking['booking_date']} {booking['booking_time']}</p>
                        <p><strong>كود الحجز:</strong> {booking['booking_code']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("لا توجد حجوزات تحت هذا الرقم")


def render_admin_page() -> None:
    """لوحة التحكم الإدارية"""
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    render_page_banner(
        "لوحة التحكم",
        "إدارة الحجوزات والأدوار",
        "إدارة",
        "⚙️"
    )
    
    if not st.session_state.admin_logged_in:
        pin = st.text_input("أدخل رمز المسؤول:", type="password")
        if pin == ADMIN_PIN:
            st.session_state.admin_logged_in = True
            st.rerun()
        elif pin:
            st.error("رمز المسؤول غير صحيح")
        return
    
    if st.button("تسجيل الخروج"):
        st.session_state.admin_logged_in = False
        st.rerun()
    
    today_str = dt.date.today().isoformat()
    summary = get_dashboard_summary(today_str)
    
    render_stat_cards([
        ("الحجوزات اليوم", str(summary["total_bookings"]), "📅"),
        ("بانتظار الخدمة", str(summary["waiting_count"]), "⏳"),
        ("الإيراد", f"EGP {summary['estimated_revenue']:.0f}", "💰"),
    ])
    
    st.write("")
    st.markdown('<div class="section-title">حجوزات اليوم</div>', unsafe_allow_html=True)
    
    today_bookings = fetch_all(
        """
        SELECT b.*, c.name, br.name as branch_name, s.name as service_name, st.name as staff_name
        FROM bookings b
        INNER JOIN customers c ON b.customer_id = c.id
        INNER JOIN branches br ON b.branch_id = br.id
        INNER JOIN services s ON b.service_id = s.id
        INNER JOIN staff st ON b.staff_id = st.id
        WHERE b.booking_date = ?
        """,
        (today_str,),
    )
    
    if today_bookings:
        df = pd.DataFrame([dict(b) for b in today_bookings])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد حجوزات في هذا اليوم")


# ============ MAIN APPLICATION ============
def main() -> None:
    """التطبيق الرئيسي"""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="✂️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    inject_professional_css()
    
    # تهيئة قاعدة البيانات
    init_db()
    
    # الشريط الجانبي
    st.sidebar.markdown(f"## {APP_TITLE}")
    
    page = st.sidebar.radio(
        "اختر الصفحة:",
        ["الرئيسية", "احجز الآن", "ابحث عن حجزك", "لوحة التحكم"],
    )
    
    if page == "الرئيسية":
        render_home()
    elif page == "احجز الآن":
        render_booking_page()
    elif page == "ابحث عن حجزك":
        render_lookup_page()
    elif page == "لوحة التحكم":
        render_admin_page()


if __name__ == "__main__":
    main()
