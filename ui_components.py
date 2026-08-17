"""
UI Components and styling for Streamlit
"""
import streamlit as st
from typing import Any, Optional

from config import DEFAULT_LANGUAGE


def inject_custom_css() -> None:
    """Inject custom CSS styling for the app"""
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
    """Render page hero banner"""
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
    """Render stat cards in columns"""
    columns = st.columns(len(items))
    for col, (label, value) in zip(columns, items):
        with col:
            st.markdown(
                f'<div class="mini-stat"><h4>{label}</h4><p>{value}</p></div>',
                unsafe_allow_html=True,
            )


def render_soft_card(title: str, content: str) -> None:
    """Render a soft card with title and content"""
    st.markdown(
        f"""
        <div class="soft-card">
            <div class="section-title">{title}</div>
            <div class="quick-info">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ticket_card(title: str, content: str) -> None:
    """Render a ticket/highlight card"""
    st.markdown(
        f"""
        <div class="ticket-card">
            <div class="section-title">{title}</div>
            <div class="quick-info">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_branch_card(name: str, category: str, location: str, hours: str, service_count: int) -> None:
    \"\"\"Render a branch info card\"\"\"
    st.markdown(
        f\"\"\"
        <div class="branch-card">
            <h4>{name}</h4>
            <p>النوع: {category}</p>
            <p>الموقع: {location}</p>
            <p>ساعات العمل: {hours}</p>
            <p>عدد الخدمات: {service_count}</p>
        </div>
        \"\"\",
        unsafe_allow_html=True,
    )


def render_step_cards(steps: list[tuple[str, str]]) -> None:
    \"\"\"Render step cards in columns\"\"\"
    columns = st.columns(len(steps))
    for col, (title, description) in zip(columns, steps):
        with col:
            st.markdown(
                f\"\"\"
                <div class="step-card">
                    <h4>{title}</h4>
                    <p>{description}</p>
                </div>
                \"\"\",
                unsafe_allow_html=True,
            )


def get_language_from_session() -> str:
    \"\"\"Get current language from session state\"\"\"
    return st.session_state.get(\"lang\", DEFAULT_LANGUAGE)


def localized_value(ar_value: str | None, en_value: str | None) -> str:
    \"\"\"Get localized value based on current language\"\"\"
    lang = get_language_from_session()
    if lang == \"ar\":
        return ar_value or en_value or \"\"
    return en_value or ar_value or \"\"
