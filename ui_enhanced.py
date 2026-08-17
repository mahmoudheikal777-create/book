"""
Enhanced Styling for Glow & Groom - Professional Design System
"""
import streamlit as st


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
                --radius-sm: 8px;
                --radius-md: 12px;
                --radius-lg: 16px;
                --radius-xl: 24px;
                --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
                --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
                --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
                --shadow-xl: 0 20px 25px rgba(0,0,0,0.1);
            }
            
            * {
                font-family: 'Cairo', 'Poppins', sans-serif;
            }
            
            html {
                direction: rtl;
                scroll-behavior: smooth;
            }
            
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
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
            
            /* ===== SIDEBAR ===== */
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
                border-radius: var(--radius-md);
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
            
            /* ===== PAGE HERO ===== */
            .page-hero {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: var(--radius-xl);
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
                backdrop-filter: blur(10px);
                letter-spacing: 0.5px;
            }
            
            /* ===== ANIMATIONS ===== */
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
                0%, 100% {
                    transform: translateY(0px);
                }
                50% {
                    transform: translateY(-20px);
                }
            }
            
            @keyframes pulse {
                0%, 100% {
                    opacity: 1;
                }
                50% {
                    opacity: 0.8;
                }
            }
            
            @keyframes shimmer {
                0% {
                    background-position: -1000px 0;
                }
                100% {
                    background-position: 1000px 0;
                }
            }
            
            /* ===== STAT CARDS ===== */
            .stat-card {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(99,102,241,0.1);
                border-radius: var(--radius-lg);
                padding: 1.5rem 1.25rem;
                box-shadow: var(--shadow-lg);
                backdrop-filter: blur(10px);
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
                background: rgba(255,255,255,0.98);
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
            
            /* ===== CARDS ===== */
            .soft-card, .ticket-card {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(148,163,184,0.2);
                border-radius: var(--radius-lg);
                padding: 1.5rem;
                box-shadow: var(--shadow-md);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                animation: slideInUp 0.6s ease;
            }
            
            .soft-card:hover {
                border-color: rgba(99,102,241,0.3);
                box-shadow: var(--shadow-lg);
                transform: translateY(-4px);
            }
            
            .ticket-card {
                background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(236,72,153,0.1) 100%);
                border: 1px solid rgba(99,102,241,0.2);
                position: relative;
            }
            
            .ticket-card::before {
                content: '✓';
                position: absolute;
                top: 1rem;
                right: 1.5rem;
                font-size: 1.5rem;
                color: var(--success);
            }
            
            /* ===== SECTION TITLES ===== */
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
            
            /* ===== BRANCH CARDS ===== */
            .branch-card {
                background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.96) 100%);
                border: 1px solid rgba(148,163,184,0.2);
                border-radius: var(--radius-lg);
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
            
            .branch-card::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200px;
                height: 200px;
                background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);
                border-radius: 50%;
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
                position: relative;
                z-index: 2;
            }
            
            .branch-card p {
                margin: 0.4rem 0;
                color: var(--gray-600);
                font-size: 0.9rem;
                position: relative;
                z-index: 2;
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
            
            /* ===== STEP CARDS ===== */
            .step-card {
                background: rgba(255,255,255,0.9);
                border: 2px dashed rgba(99,102,241,0.3);
                border-radius: var(--radius-lg);
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
            
            /* ===== FORMS ===== */
            div[data-testid="stForm"], 
            div[data-testid="stFormSubmitButton"] {
                border-radius: var(--radius-lg) !important;
            }
            
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            div[data-baseweb="select"] {
                border-radius: var(--radius-md) !important;
                border: 1px solid var(--gray-300) !important;
                padding: 10px 12px !important;
                font-size: 0.95rem !important;
                transition: all 0.3s ease !important;
            }
            
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {
                border-color: var(--primary) !important;
                box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
            }
            
            /* ===== BUTTONS ===== */
            .stButton > button, 
            .stDownloadButton > button, 
            .stFormSubmitButton > button {
                border-radius: var(--radius-md) !important;
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
            .stDownloadButton > button:hover, 
            .stFormSubmitButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 20px rgba(99,102,241,0.4) !important;
            }
            
            .stButton > button:active, 
            .stDownloadButton > button:active, 
            .stFormSubmitButton > button:active {
                transform: translateY(0) !important;
            }
            
            /* ===== ALERTS ===== */
            .stAlert {
                border-radius: var(--radius-lg) !important;
                border-left: 4px solid !important;
                padding: 1rem !important;
                animation: slideInUp 0.3s ease !important;
            }
            
            .stAlert > div {
                font-size: 0.95rem !important;
            }
            
            [data-testid="stNotification"] {
                border-radius: var(--radius-lg) !important;
                box-shadow: var(--shadow-lg) !important;
            }
            
            /* ===== METRICS ===== */
            div[data-testid="stMetric"] {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(148,163,184,0.2);
                padding: 1.25rem;
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                transition: all 0.3s ease;
            }
            
            div[data-testid="stMetric"]:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }
            
            /* ===== DATAFRAME ===== */
            div[data-testid="stDataFrame"] {
                border-radius: var(--radius-lg) !important;
                overflow: hidden;
                box-shadow: var(--shadow-md);
            }
            
            /* ===== TABS ===== */
            div[data-testid="stTabs"] {
                background: transparent;
            }
            
            [data-baseweb="tab-list"] {
                border-bottom: 2px solid var(--gray-200) !important;
                padding-bottom: 0 !important;
            }
            
            [data-baseweb="tab"] {
                border-radius: 0 !important;
                border-bottom: 3px solid transparent !important;
                margin-bottom: -2px !important;
                color: var(--gray-600) !important;
                transition: all 0.3s ease !important;
            }
            
            [data-baseweb="tab"]:hover {
                color: var(--primary) !important;
            }
            
            [aria-selected="true"] {
                border-color: var(--primary) !important;
                color: var(--primary) !important;
            }
            
            /* ===== SELECTBOX ===== */
            div[data-baseweb="select"] > div:first-child {
                border-radius: var(--radius-md) !important;
                border: 1px solid var(--gray-300) !important;
            }
            
            /* ===== BALLOONS ===== */
            .stBalloons {
                animation: float 3s ease-in-out infinite !important;
            }
            
            /* ===== LOADING ===== */
            .stSpinner > div {
                border-color: var(--primary) !important;
                border-right-color: transparent !important;
            }
            
            /* ===== SCROLLBAR ===== */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: transparent;
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--gray-400);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--gray-500);
            }
            
            /* ===== RESPONSIVE ===== */
            @media (max-width: 768px) {
                .page-hero h1 {
                    font-size: 1.75rem;
                }
                
                .page-hero p {
                    font-size: 0.95rem;
                    max-width: 100%;
                }
                
                .section-title {
                    font-size: 1.1rem;
                }
                
                .stat-card {
                    min-height: 120px;
                }
                
                .branch-card {
                    min-height: 200px;
                }
            }
            
            /* ===== DARK MODE SUPPORT ===== */
            @media (prefers-color-scheme: dark) {
                .stApp {
                    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
                }
                
                .soft-card, .ticket-card {
                    background: rgba(30, 27, 75, 0.95);
                    border-color: rgba(99, 102, 241, 0.2);
                    color: #e0e7ff;
                }
                
                .page-hero {
                    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                }
                
                .branch-card {
                    background: rgba(30, 27, 75, 0.98);
                }
                
                .section-title {
                    color: #e0e7ff;
                }
                
                .quick-info {
                    color: #cbd5e1;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(label: str, value: str, icon: str = "📊") -> None:
    """Render a single stat card with icon"""
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


def render_stat_cards_row(items: list[tuple[str, str, str]]) -> None:
    """Render stat cards in a responsive row"""
    cols = st.columns(len(items))
    for col, (label, value, icon) in zip(cols, items):
        with col:
            render_stat_card(label, value, icon)


def render_page_banner(title: str, subtitle: str, badge: str, emoji: str = "✂️") -> None:
    """Render page hero banner"""
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="subtle-badge">{badge}</div>
            <h1>{emoji} {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_soft_card(title: str, content: str, icon: str = "ℹ️") -> None:
    """Render a soft card with title and content"""
    st.markdown(
        f"""
        <div class="soft-card">
            <div class="section-title">{icon} {title}</div>
            <div class="quick-info">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ticket_card(title: str, content: str, icon: str = "✅") -> None:
    """Render a ticket/highlight card"""
    st.markdown(
        f"""
        <div class="ticket-card">
            <div class="section-title">{icon} {title}</div>
            <div class="quick-info">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_cards(steps: list[tuple[str, str, str]]) -> None:
    """Render step cards with icons"""
    columns = st.columns(len(steps))
    for col, (title, description, icon) in zip(columns, steps):
        with col:
            st.markdown(
                f"""
                <div class="step-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                    <h4>{title}</h4>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_branch_card(name: str, category: str, location: str, hours: str, service_count: int, icon: str = "🏢") -> None:
    """Render a branch card"""
    st.markdown(
        f"""
        <div class="branch-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <h4>{name}</h4>
            <p>📂 {category}</p>
            <p>📍 {location}</p>
            <p>⏰ {hours}</p>
            <p>💼 {service_count} خدمات</p>
            <div class="badge">متاح الآن</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_loading_state(message: str = "جاري التحميل...") -> None:
    """Render a loading state"""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⏳</div>
            <p style="color: var(--gray-600); font-size: 1rem;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, message: str, icon: str = "📭") -> None:
    """Render an empty state"""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="color: var(--gray-800); font-size: 1.3rem; margin-bottom: 0.5rem;">{title}</h3>
            <p style="color: var(--gray-600); font-size: 0.95rem;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_success_message(title: str, booking_details: dict) -> None:
    """Render a detailed success message"""
    st.markdown(
        f"""
        <div class="ticket-card" style="border-left: 4px solid var(--success); padding: 2rem;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
                <div class="section-title" style="justify-content: center;">{title}</div>
            </div>
            <div class="quick-info">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                    <div>
                        <strong style="color: var(--gray-700);">كود الحجز</strong>
                        <p style="color: var(--primary); font-size: 1.1rem; font-weight: 700; margin: 0.5rem 0 0;">{booking_details.get('booking_code', 'N/A')}</p>
                    </div>
                    <div>
                        <strong style="color: var(--gray-700);">رقم الدور</strong>
                        <p style="color: var(--primary); font-size: 1.1rem; font-weight: 700; margin: 0.5rem 0 0;">#{booking_details.get('queue_number', 'N/A')}</p>
                    </div>
                    <div>
                        <strong style="color: var(--gray-700);">الفرع</strong>
                        <p style="margin: 0.5rem 0 0;">{booking_details.get('branch_name', 'N/A')}</p>
                    </div>
                    <div>
                        <strong style="color: var(--gray-700);">الخدمة</strong>
                        <p style="margin: 0.5rem 0 0;">{booking_details.get('service_name', 'N/A')}</p>
                    </div>
                    <div>
                        <strong style="color: var(--gray-700);">الموظف</strong>
                        <p style="margin: 0.5rem 0 0;">{booking_details.get('staff_name', 'N/A')}</p>
                    </div>
                    <div>
                        <strong style="color: var(--gray-700);">الموعد</strong>
                        <p style="margin: 0.5rem 0 0;">{booking_details.get('date', 'N/A')} - {booking_details.get('time', 'N/A')}</p>
                    </div>
                    <div>
                        <strong style="color: var(--gray-700);">السعر</strong>
                        <p style="color: var(--success); font-size: 1.1rem; font-weight: 700; margin: 0.5rem 0 0;">{booking_details.get('price', 'N/A'):.0f} EGP</p>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
