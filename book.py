import streamlit as st
import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Smart Booking System", page_icon="📅", layout="centered")

st.title("✂️ Smart Booking & Queue System")
st.write("Book your appointment easily and track your live queue position!")

# قائمة الخدمات أو الأماكن
service_provider = st.selectbox(
    "Select Service Provider / Branch:",
    ["Star Salon (Men's Grooming)", "Smile Dental Clinic", "Royal Beauty Center"]
)

st.divider()

# قسم الحجز (Booking Form)
st.subheader("📝 Book an Appointment")

with st.form("booking_form"):
    client_name = st.text_input("Your Full Name:")
    client_phone = st.text_input("Phone Number:")
    
    col1, col2 = st.columns(2)
    with col1:
        booking_date = st.date_input("Select Date:", min_value=datetime.date.today())
    with col2:
        booking_time = st.selectbox("Select Time Slot:", ["12:00 PM", "02:00 PM", "04:00 PM", "06:00 PM", "08:00 PM", "10:00 PM"])
    
    submit_button = st.form_submit_button(label="Confirm Booking 🚀")

    if submit_button:
        if client_name.strip() == "" or client_phone.strip() == "":
            st.error("⚠️ Please enter your name and phone number correctly!")
        else:
            # محاكاة توليد رقم دور عشوائي بناءً على الوقت
            queue_number = 5 
            st.success(f"🎉 Success, {client_name}! Your booking at ({service_provider}) is confirmed.")
            st.info(f"🎫 Your Queue Ticket Number is: **#{queue_number}**")
            st.balloons()

st.divider()

# ميزة معرفة الدور الحالي (Live Queue Tracking)
st.subheader("📊 Live Queue Tracker (Check Your Turn)")
st.write("Check who is currently being served right now in real-time:")

# زر لتحديث أو عرض الدور الحالي
if st.button("Refresh Queue Status"):
    # محاكاة رقم الدور الحالي في المحل
    current_serving = 3
    st.metric(label="Now Serving Turn Number", value=f"#{current_serving}")
    st.warning("⚠️ If your ticket number is close, please be ready at the venue!")

st.divider()

# لوحة تحكم صاحب المحل (Dashboard)
with st.expander("🔐 Business Owner Dashboard"):
    st.write("Manage today's appointments and update the current serving turn:")
    new_turn = st.number_input("Update Current Serving Number:", min_value=1, max_value=50, value=3)
    if st.button("Update Turn on Screen"):
        st.success(f"✅ Live queue updated successfully to #{new_turn}!")
