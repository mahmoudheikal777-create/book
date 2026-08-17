"""
Glow & Groom Booking Hub - Main Application
Refactored version with clean separation of concerns
"""
from datetime import date
import streamlit as st

from config import (
    APP_ICON,
    APP_SUBTITLE,
    APP_TITLE,
    ADMIN_PIN,
    DEFAULT_LANGUAGE,
    get_message,
)
from database import db
from seed_data import seed_demo_data
from services import (
    BranchService,
    BookingService,
    CustomerService,
    DashboardService,
    QueueService,
    ServiceService,
    TimeSlotService,
)
from ui_components import (
    get_language_from_session,
    inject_custom_css,
    render_branch_card,
    render_page_banner,
    render_soft_card,
    render_stat_cards,
    render_step_cards,
    render_ticket_card,
)


# ==================== Session Management ====================
def init_session_state() -> None:
    \"\"\"Initialize session state variables\"\"\"
    if \"lang\" not in st.session_state:
        st.session_state.lang = DEFAULT_LANGUAGE
    if \"admin_ok\" not in st.session_state:
        st.session_state.admin_ok = False


# ==================== Home Page ====================
def render_home() -> None:
    \"\"\"Render home/landing page\"\"\"
    today_str = date.today().isoformat()
    branches = BranchService.get_all_branches()
    services_count = len([s for b in branches for s in ServiceService.get_services(b.id)])
    summary = DashboardService.get_dashboard_summary(today_str)

    # Hero section
    render_page_banner(
        "منصة حجز صالونات سهلة وواضحة",
        "واجهة عربية عملية تنقل العميل من اختيار الفرع والخدمة إلى تأكيد الحجز ومتابعة دوره بدون تعقيد.",
        "تجربة استخدام جديدة",
    )
    render_stat_cards(
        [
            ("عدد الفروع", str(len(branches))),
            ("الخدمات المتاحة", str(services_count)),
            ("حجوزات اليوم", str(summary.total_bookings)),
        ]
    )

    st.write("")
    left, right = st.columns([1.2, 1])

    with left:
        render_soft_card(
            "كيف يعمل النظام؟",
            """
            1. يختار العميل الفرع والخدمة المناسبة له.<br>
            2. يرى فقط المواعيد المتاحة فعلًا حسب الموظفين والطاقة التشغيلية.<br>
            3. يحصل مباشرة على كود الحجز ورقم الدور واسم الموظف المخصص له.<br><br>
            الواجهة الجديدة تركز على السرعة والوضوح وتقليل الخطوات غير المهمة.
            """,
        )

    with right:
        render_stat_cards(
            [
                ("العملاء بانتظار الخدمة", str(summary.waiting_count)),
                ("الإيراد التقديري", f"{summary.estimated_revenue:.0f} EGP"),
            ]
        )

    st.write("")
    st.markdown('<div class="section-title">ابدأ في 3 خطوات</div>', unsafe_allow_html=True)
    render_step_cards(
        [
            ("1. اختر الفرع", "كل فرع يعرض خدماته ومواعيد التشغيل الخاصة به بشكل مستقل."),
            ("2. حدد الخدمة", "يتم عرض السعر والمدة تلقائيًا لمساعدة العميل على القرار بسرعة."),
            ("3. أكد الموعد", "النظام يولد رقم الدور ويخصص موظفًا متاحًا تلقائيًا."),
        ]
    )

    st.write("")
    st.markdown('<div class="section-title">الفروع المتاحة</div>', unsafe_allow_html=True)
    branch_cols = st.columns(len(branches))
    for col, branch in zip(branch_cols, branches):
        with col:
            branch_services = ServiceService.get_services(branch.id)
            render_branch_card(
                branch.name,
                branch.category,
                branch.location,
                branch.hours_display(),
                len(branch_services),
            )


# ==================== Booking Page ====================
def render_booking_page() -> None:
    \"\"\"Render booking page\"\"\"
    render_page_banner(
        "حجز سريع وواضح",
        "قسم الحجز مصمم بحيث يرى العميل الفرع والخدمة والموعد الملائم قبل إدخال بياناته.",
        "تجربة الحجز",
    )

    branches = BranchService.get_all_branches()
    branch_options = {f\"{b.name} - {b.location}\": b for b in branches}

    # Selection row
    col1, col2, col3 = st.columns([1.1, 1.2, 1])

    with col1:
        branch_label = st.selectbox("الفرع", list(branch_options), key=\"book_branch\")
    selected_branch = branch_options[branch_label]

    with col2:
        services = ServiceService.get_services(selected_branch.id)
        service_options = {
            f\"{s.name} | {s.duration_display()} | {s.price_display()}\": s
            for s in services
        }
        service_label = st.selectbox("الخدمة", list(service_options), key=\"book_service\")
    selected_service = service_options[service_label]

    with col3:
        selected_date = st.date_input("التاريخ", min_value=date.today(), key=\"book_date\")

    date_str = selected_date.isoformat()

    # Get available slots
    slots = TimeSlotService.generate_available_slots(
        selected_branch.id,
        selected_service.id,
        date_str,
    )

    staff_count = len([s for s in ServiceService.get_services(selected_branch.id)])

    # Stats
    render_stat_cards(
        [
            ("السعر", selected_service.price_display()),
            ("مدة الخدمة", selected_service.duration_display()),
            ("المواعيد المتاحة", str(len(slots))),
            ("الموظفون", str(staff_count)),
        ]
    )

    # Booking form
    info_col, form_col = st.columns([0.95, 1.35])

    with info_col:
        render_soft_card(
            "ملخص الاختيار",
            f"""
            الفرع: <strong>{selected_branch.name}</strong><br>
            الموقع: <strong>{selected_branch.location}</strong><br>
            الخدمة: <strong>{selected_service.name}</strong><br>
            مدة الخدمة: <strong>{selected_service.duration_display()}</strong><br>
            السعر: <strong>{selected_service.price_display()}</strong><br>
            التاريخ: <strong>{date_str}</strong><br><br>
            يتم تخصيص الموظف تلقائيًا حسب أول شخص متاح للخدمة في الوقت المختار.
            """,
        )
        st.write("")
        render_soft_card(
            "نصيحة لتجربة أفضل",
            "اختر الموعد الأقرب إذا كان هدفك سرعة الإنجاز، أو اختر تاريخًا لاحقًا إذا أردت مرونة أكبر في الأوقات المتاحة.",
        )

    with form_col:
        with st.form("booking_form\"):
            st.markdown('<div class="section-title">بيانات العميل</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                client_name = st.text_input("الاسم الكامل", key=\"book_name\")
            with col2:
                client_phone = st.text_input("رقم الهاتف", key=\"book_phone\")

            if slots:
                booking_time = st.selectbox("اختر الموعد المتاح", slots, key=\"book_time\")
            else:
                booking_time = None
                st.warning("لا توجد مواعيد متاحة لهذا اليوم مع هذه الخدمة.")

            notes = st.text_area(
                "ملاحظات إضافية",
                placeholder="مثال: يفضل موظف هادئ أو خدمة سريعة",
                key=\"book_notes\",
            )

            submitted = st.form_submit_button("تأكيد الحجز الآن")

            if submitted:
                if not client_name.strip() or not client_phone.strip():
                    st.error("يرجى إدخال الاسم ورقم الهاتف بشكل صحيح.")
                elif booking_time is None:
                    st.error("اختر يومًا آخر أو خدمة أخرى لوجود ازدحام كامل.")
                else:
                    result = BookingService.create_booking(
                        client_name,
                        client_phone,
                        selected_branch.id,
                        selected_service.id,
                        date_str,
                        booking_time,
                        notes,
                        get_language_from_session(),
                    )

                    if result.success:
                        st.success(result.message)
                        details = result.booking_details
                        render_ticket_card(
                            "تم تأكيد الحجز",
                            f\"\"\"
                            كود الحجز: <strong>{details['booking_code']}</strong><br>
                            رقم الدور: <strong>#{details['queue_number']}</strong><br>
                            الفرع: <strong>{details['branch_name']}</strong><br>
                            الخدمة: <strong>{details['service_name']}</strong><br>
                            الموظف المخصص: <strong>{details['staff_name']}</strong><br>
                            الموعد: <strong>{details['date']} - {details['time']}</strong><br>
                            السعر: <strong>{details['price']:.0f} EGP</strong>
                            \"\"\",
                        )
                        st.balloons()
                    else:
                        st.error(result.message)


# ==================== Lookup Page ====================
def render_lookup_page() -> None:
    \"\"\"Render customer lookup page\"\"\"
    render_page_banner(
        "استعلام سريع عن حجوزات العميل",
        "أدخل رقم الهاتف للوصول إلى كل الحجوزات السابقة والقادمة.",
        "متابعة العميل",
    )

    phone = st.text_input("رقم الهاتف المستخدم في الحجز", key=\"lookup_phone\")

    if st.button("بحث عن الحجوزات"):
        if not phone.strip():
            st.error("يرجى إدخال رقم هاتف.")
            return

        bookings = CustomerService.get_customer_bookings(phone)

        if not bookings:
            st.warning("لا توجد حجوزات مرتبطة بهذا الرقم.")
            return

        render_soft_card(
            "نتيجة البحث",
            f\"تم العثور على <strong>{len(bookings)}</strong> حجز مرتبط بهذا الرقم.\",
        )
        st.write("")

        for booking in bookings:
            render_soft_card(
                booking.service_name,
                f\"\"\"
                الفرع: <strong>{booking.branch_name}</strong><br>
                كود الحجز: <strong>{booking.booking_code}</strong><br>
                الموعد: <strong>{booking.booking_date} - {booking.booking_time}</strong><br>
                الموظف: <strong>{booking.staff_name}</strong><br>
                رقم الدور: <strong>#{booking.queue_number}</strong><br>
                الحالة: <strong>{booking.status}</strong>
                \"\"\",
            )


# ==================== Queue Page ====================
def render_queue_page() -> None:
    \"\"\"Render queue tracking page\"\"\"
    render_page_banner(
        "الطابور المباشر",
        "تابع رقم الدور الحالي في كل فرع بشكل واضح وسريع.",
        "متابعة لحظية",
    )

    branches = BranchService.get_all_branches()
    branch_options = {b.name: b for b in branches}

    col1, col2 = st.columns([1.2, 1])
    with col1:
        selected_branch_name = st.selectbox("اختر الفرع", list(branch_options), key=\"queue_branch\")
    branch = branch_options[selected_branch_name]

    with col2:
        selected_date = st.date_input("تاريخ المتابعة", value=date.today(), key=\"queue_date\")

    date_str = selected_date.isoformat()

    # Get queue info
    current_serving = QueueService.get_queue_status(branch.id, date_str)
    bookings = BookingService.get_branch_bookings(branch.id, date_str)
    waiting = [b for b in bookings if b.queue_number >= current_serving]

    render_stat_cards(
        [
            ("الدور الحالي", f\"#{current_serving}\"),
            ("إجمالي الحجوزات", str(len(bookings))),
            ("المتبقي في الانتظار", str(len(waiting))),
        ]
    )

    if waiting:
        render_soft_card(
            "معلومة سريعة",
            f\"\"\"
            الفرع الحالي: <strong>{branch.name}</strong><br>
            أول عميل في الانتظار يحمل رقم <strong>#{waiting[0].queue_number}</strong>.
            \"\"\",
        )
        st.write("")
        st.markdown('<div class="section-title">العملاء القادمون</div>', unsafe_allow_html=True)

        preview_data = [
            {
                "رقم الدور": f\"#{b.queue_number}\",
                "العميل": b.customer_name,
                "الخدمة": b.service_name,
                "الوقت": b.booking_time,
                "الموظف": b.staff_name,
            }
            for b in waiting[:8]
        ]
        st.dataframe(preview_data, use_container_width=True, hide_index=True)
    else:
        st.info("لا يوجد عملاء في قائمة الانتظار لهذا اليوم.")


# ==================== Admin Page ====================
def render_admin_page() -> None:
    \"\"\"Render admin dashboard page\"\"\"
    render_page_banner(
        "لوحة إدارة التشغيل",
        "واجهة إدارية لمتابعة الحجوزات اليومية وتحديث رقم الدور.",
        "إدارة الفرع",
    )

    if not st.session_state.admin_ok:
        render_soft_card(
            "تسجيل دخول الإدارة",
            "أدخل كود الإدارة للوصول إلى أدوات التحكم الخاصة بالفروع.",
        )

        pin = st.text_input("كود الإدارة", type=\"password\", key=\"admin_pin\")
        col1, col2 = st.columns([1, 1.4])

        with col1:
            if st.button("دخول لوحة الإدارة"):
                if pin == ADMIN_PIN:
                    st.session_state.admin_ok = True
                    st.success("تم فتح لوحة الإدارة.")
                    st.rerun()
                else:
                    st.error(get_message(\"wrong_pin\", get_language_from_session()))

        with col2:
            st.info("الكود الافتراضي للتجربة: 1234")
        return

    # Admin is logged in
    branches = BranchService.get_all_branches()
    branch_options = {b.name: b for b in branches}

    top1, top2, top3 = st.columns([1.2, 1, 0.8])

    with top1:
        selected_branch_name = st.selectbox(
            "اختر الفرع",
            list(branch_options),
            key=\"admin_branch\",
        )
    branch = branch_options[selected_branch_name]

    with top2:
        selected_date = st.date_input(
            "تاريخ التشغيل",
            value=date.today(),
            key=\"admin_date\",
        )

    date_str = selected_date.isoformat()

    with top3:
        if st.button("تسجيل الخروج"):
            st.session_state.admin_ok = False
            st.rerun()

    # Get admin data
    bookings = BookingService.get_branch_bookings(branch.id, date_str)
    current_serving = QueueService.get_queue_status(branch.id, date_str)
    estimated_revenue = sum(b.service_price for b in bookings if b.service_price)

    render_stat_cards(
        [
            ("حجوزات الفرع", str(len(bookings))),
            ("الدور الحالي", f\"#{current_serving}\"),
            ("الإيراد التقديري", f\"{estimated_revenue:.0f} EGP\"),
        ]
    )

    # Tabs
    tab_summary, tab_queue, tab_bookings = st.tabs(
        [\"ملخص التشغيل\", \"إدارة الطابور\", \"حجوزات اليوم\"]
    )

    with tab_summary:
        render_soft_card(
            "ملخص الفرع",
            f\"\"\"
            الفرع: <strong>{branch.name}</strong><br>
            الموقع: <strong>{branch.location}</strong><br>
            النوع: <strong>{branch.category}</strong><br>
            ساعات العمل: <strong>{branch.hours_display()}</strong><br>
            تاريخ التشغيل: <strong>{date_str}</strong>
            \"\"\",
        )
        st.write(\"\")

        if bookings:
            next_customer = next(
                (b for b in bookings if b.queue_number >= current_serving),
                bookings[0],
            )
            render_ticket_card(
                "أقرب عميل للتجهيز",
                f\"\"\"
                العميل: <strong>{next_customer.customer_name}</strong><br>
                الخدمة: <strong>{next_customer.service_name}</strong><br>
                الوقت: <strong>{next_customer.booking_time}</strong><br>
                رقم الدور: <strong>#{next_customer.queue_number}</strong>
                \"\"\",
            )
        else:
            st.info("لا توجد حجوزات حتى الآن لهذا التاريخ.")

    with tab_queue:
        render_soft_card(
            "تحديث رقم الدور",
            "حدّث الرقم الحالي بمجرد انتقال الخدمة للعميل التالي.",
        )

        next_turn = st.number_input(
            "رقم الدور الذي يتم خدمته الآن",
            min_value=1,
            max_value=max(len(bookings) + 5, 10),
            value=max(current_serving, 1),
        )

        if st.button("حفظ تحديث الدور"):
            if QueueService.set_queue_status(branch.id, date_str, int(next_turn)):
                st.success(get_message(\"queue_updated\", queue_number=int(next_turn)))
            else:
                st.error("فشل تحديث الدور.")

    with tab_bookings:
        if bookings:
            table_data = [
                {
                    \"رقم الدور\": b.queue_number,
                    \"كود الحجز\": b.booking_code,
                    \"العميل\": b.customer_name,
                    \"الهاتف\": b.customer_phone,
                    \"الخدمة\": b.service_name,
                    \"الموظف\": b.staff_name,
                    \"الوقت\": b.booking_time,
                    \"الحالة\": b.status,
                }
                for b in bookings
            ]
            st.dataframe(table_data, use_container_width=True, hide_index=True)

            # Export as CSV
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=table_data[0].keys())
            writer.writeheader()
            writer.writerows(table_data)

            st.download_button(
                \"تحميل تقرير CSV\",
                data=output.getvalue(),
                file_name=f\"bookings_{branch.id}_{date_str}.csv\",
                mime=\"text/csv\",
            )
        else:
            st.info(\"لا توجد حجوزات لهذا الفرع في التاريخ المحدد.\")


# ==================== Main App ====================
def main() -> None:
    \"\"\"Main app entry point\"\"\"
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout=\"wide\")

    # Initialize database and session
    db.init_schema()
    seed_demo_data()
    init_session_state()
    inject_custom_css()

    # Header
    st.title(f\"{APP_ICON} {APP_TITLE}\")
    st.caption(APP_SUBTITLE)

    # Sidebar navigation
    with st.sidebar:
        st.header(\"القائمة الرئيسية\")

        page = st.radio(
            \"انتقل إلى\",
            [
                \"الرئيسية\",
                \"احجز الآن\",
                \"استعلام العميل\",
                \"الطابور المباشر\",
                \"لوحة الإدارة\",
            ],
        )

        st.markdown(\"---\")
        st.markdown(
            \"\"\"
            **ماذا يقدم النظام؟**

            - حجز سريع بخطوات قليلة
            - عرض مواعيد متاحة فعلية
            - متابعة الدور الحالي
            - لوحة إدارة سهلة
            \"\"\"
        )
        st.info(
            \"يتم حفظ البيانات محليًا داخل SQLite، ويمكن تطوير التطبيق لاحقًا ليدعم تعدد المستخدمين والفروع.\"
        )

    # Route to page
    if page == \"الرئيسية\":
        render_home()
    elif page == \"احجز الآن\":
        render_booking_page()
    elif page == \"استعلام العميل\":
        render_lookup_page()
    elif page == \"الطابور المباشر\":
        render_queue_page()
    else:
        render_admin_page()


if __name__ == \"__main__\":
    main()
