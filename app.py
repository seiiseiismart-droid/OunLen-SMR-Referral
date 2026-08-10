import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Appointment Booking",
    page_icon="📅",
    layout="wide"
)

# ----------------------------------------------------------------
# 2. Check URL Parameters (ពិនិត្យមើលថាជា Link អតិថិជន ឬ Admin)
# ----------------------------------------------------------------
query_params = st.query_params
is_client_view = query_params.get("mode") == "client"

# ----------------------------------------------------------------
# 3. Main Navigation / Mode Switching
# ----------------------------------------------------------------
if is_client_view:
    # ប្រសិនបើជា Link របស់អតិថិជន (?mode=client)
    selected_menu = "📅 កក់ម៉ោងថ្មី (New Booking)"
else:
    # ប្រសិនបើជា Admin/Staff (បង្ហាញ Radio Menu ទាំងមូល)
    selected_menu = st.radio(
        "📌 Navigation Menu",
        [
            "📅 កក់ម៉ោងថ្មី (New Booking)",
            "📋 បញ្ជីកក់ម៉ោង (Manage Bookings)",
            "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)",
            "👩‍ពីរ ស្ទាត់ជំនាញ គ្រប់គ្រងបុគ្គលិក (Staff)",
            "📊 របាយការណ៍កក់ (Booking Report)"
        ],
        horizontal=True
    )
    st.markdown("---")

# ----------------------------------------------------------------
# 4. Form សម្រាប់កក់ម៉ោង (Customer Booking View)
# ----------------------------------------------------------------
if selected_menu == "📅 កក់ម៉ោងថ្មី (New Booking)":
    
    # 标题 និង Link សម្រាប់ Share ទៅកាន់អតិថិជន (បង្ហាញតែ Admin)
    col_title, col_link = st.columns([3, 1])
    with col_title:
        st.title("📅 បង្កើតការកក់ម៉ោងថ្មី (New Appointment)")
    
    if not is_client_view:
        with col_link:
            st.info("🔗 **Link សម្រាប់ផ្ញើជូនអតិថិជន៖**\n`?mode=client`")

    c_form, c_summary = st.columns([2.2, 1.2], gap="large")

    with c_form:
        st.subheader("1. ព័ត៌មានអតិថិជន")
        col_c1, col_c2 = st.columns(2)
        cust_name = col_c1.text_input("ឈ្មោះអតិថិជន (Customer Name)*", placeholder="ឧទាហរណ៍: អ្នកស្រី គឹម")
        cust_phone = col_c2.text_input("លេខទូរស័ព្ទ (Phone Number)*", placeholder="ឧទាហរណ៍: 012 345 678")

        st.subheader("2. ជ្រើសរើសសេវាកម្ម & បុគ្គលិក")
        cat_type = st.selectbox("ប្រភេទសេវាកម្ម", ["✨ សេវាកម្មទូទៅ", "⚡ សេវាកម្ម Laser", "🧴 សេវាកម្ម ស្ប៉ា"])
        service_selected = st.selectbox("ជ្រើសរើសសេវាកម្ម*", [
            "ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ ($15.00 - 45នាទី)",
            "ម៉ាសស្កាតបញ្ចូលវីតាមីន Baby Glow ($15.00 - 45នាទី)",
            "ញេចសម្អាតគ្រាប់មុន ($7.50 - 30នាទី)"
        ])
        staff_selected = st.selectbox("ជ្រើសរើសជាង/បុគ្គលិក*", ["អ្នកគ្រូ ឡែន (Senior Specialist)", "កញ្ញា ម៉ារី", "ចៃដន្យ (Any Available)"])

        st.subheader("3. កាលបរិច្ឆេទ & ម៉ោងណាត់")
        col_d1, col_d2 = st.columns(2)
        book_date = col_d1.date_input("ថ្ងៃណាត់ជួប (Date)", datetime.now())
        book_time = col_d2.selectbox("ម៉ោងណាត់ជួប (Time Slot)", ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"])

        note = st.text_area("ចំណាំបន្ថែម (Note)", placeholder="ឧទាហរណ៍: ស្បែកមុខក្រហមងាយប្រប្រតិកម្ម...")

        if st.button("✅ បញ្ជាក់ការកក់ម៉ោង (Confirm Booking)", type="primary", use_container_width=True):
            if cust_name.strip() and cust_phone.strip():
                st.success("🎉 អរគុណសម្រាប់ការកក់ម៉ោង! ពួកយើងបានទទួលព័ត៌មានកក់របស់លោកអ្នករួចរាល់ហើយ។")
            else:
                st.error("សូមបញ្ចូលឈ្មោះ និង លេខទូរស័ព្ទឲ្យបានត្រឹមត្រូវ!")

    with c_summary:
        st.subheader("📄 ប័ណ្ណកក់ម៉ោងចុងក្រោយ")
        st.info("មិនទាន់មានទិន្នន័យកក់ថ្មីនៅឡើយទេ។")

# ----------------------------------------------------------------
# 5. ADMIN MODES (លាក់មិនឲ្យអតិថិជនឃើញ)
# ----------------------------------------------------------------
elif selected_menu == "📋 បញ្ជីកក់ម៉ោង (Manage Bookings)":
    st.title("📋 គ្រប់គ្រងបញ្ជីកក់ម៉ោង")
    st.write("ផ្នែកនេះសម្រាប់តែ Admin/Staff ពិនិត្យមើលការកក់ប៉ុណ្ណោះ។")

elif selected_menu == "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)":
    st.title("🛠️ គ្រប់គ្រងសេវាកម្ម")

elif selected_menu == "👩‍ពីរ ស្ទាត់ជំនាញ គ្រប់គ្រងបុគ្គលិក (Staff)":
    st.title("👩‍ពីរ គ្រប់គ្រងបុគ្គលិក")

elif selected_menu == "📊 របាយការណ៍កក់ (Booking Report)":
    st.title("📊 របាយការណ៍កក់ម៉ោង")
