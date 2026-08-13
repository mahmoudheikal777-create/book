import streamlit as st
import datetime

# إعدادات الصفحة
st.set_page_config(page_title="حجز المواعيد السريع", page_icon="📅", layout="centered")

st.title("✂️ نظام حجز المواعيد الذكي")
st.write("احجز ميعادك بسهولة من غير انتظار ومن غير مكالمات!")

# قائمة المحلات أو الخدمات المتاحة
service_provider = st.selectbox(
    "اختر الفرع أو المزود للخدمة:",
    ["صالون النجم (حلاقة رجالي)", "عيادة الدكتور للأسنان", "مركز التجميل الملكي"]
)

st.divider()

# نموذج حجز الميعاد
st.subheader("📝 بيانات الحجز")

with st.form("booking_form"):
    client_name = st.text_input("اسمك الكريم:")
    client_phone = st.text_input("رقم الهاتف:")
    
    col1, col2 = st.columns(2)
    with col1:
        booking_date = st.date_input("اختر تاريخ الحجز:", min_value=datetime.date.today())
    with col2:
        booking_time = st.selectbox("اختر الساعة:", ["12:00 م", "02:00 م", "04:00 م", "06:00 م", "08:00 م", "10:00 م"])
    
    # زر إرسال الطلب
    submit_button = st.form_submit_button(label="تأكيد الحجز الآن 🚀")

    if submit_button:
        if client_name.strip() == "" or client_phone.strip() == "":
            st.error("⚠️ من فضلك اكتب الاسم ورقم الهاتف بشكل صحيح!")
        else:
            st.success(f"🎉 مبروك يا {client_name}! تم تأكيد حجزك في ({service_provider}) يوم {booking_date} الساعة {booking_time}.")
            st.balloons() # احتفال صغير بالحجز

st.divider()

# محاكاة لوحة تحكم صاحب المحل (عشان يشوف الحجوزات)
with st.expander("🔐 لوحة تحكم صاحب المحل (لإدارة الحجوزات)"):
    st.write("هنا بيظهر لصاحب المحل كل الزبائن اللي حجزوا عنده اليومين دول:")
    st.info("📌 لا توجد حجوزات جديدة معلقة حالياً. (هذا نموذج تجريبي للمشروع)")
