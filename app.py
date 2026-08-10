import streamlit as st
import requests
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - System Booking",
    page_icon="📅",
    layout="wide"
)

# 🔗 ដាក់ Link Google Apps Script Web App របស់អ្នកនៅទីនេះ
APPS_SCRIPT_URL = "https://script.google.com/macros/s/YOUR_APPS_SCRIPT_ID_HERE/exec"

# ----------------------------------------------------------------
# 2. Check URL Parameters (Mode Selection)
# ----------------------------------------------------------------
is_client_view = st.query_params.get("mode") == "client"

if is_client_view:
    selected_menu = "📅 កក់ម៉ោងថ្មី (New Booking)"
else:
    selected_menu = st.radio(
        "📌 Navigation Menu",
        [
            "📅 កក់ម៉ោងថ្មី (New Booking)",
            "📋 បញ្ជីកក់ម៉ោង (Manage Bookings)"
        ],
        horizontal=True
    )
    st.markdown("---")

# ----------------------------------------------------------------
# 3. BOOKING FORM
# ----------------------------------------------------------------
if selected_menu == "📅 កក់ម៉ោងថ្មី (New Booking)":
    
    st.title("💇‍♀️ អូនឡែន សម្រស់ - កក់ម៉ោងសេវាកម្ម")
    st.write("សូមបំពេញព័ត៌មានខាងក្រោមដើម្បីធ្វើការកក់ម៉ោងទុកជាមុន៖")

    with st.form("booking_form", clear_on_submit=True):
        st.subheader("1. ព័ត៌មានអតិថិជន")
        c1, c2 = st.columns(2)
        cust_name = c1.text_input("ឈ្មោះអតិថិជន (Name)*", placeholder="ឧទាហរណ៍: អ្នកស្រី គឹម")
        cust_phone = c2.text_input("លេខទូរស័ព្ទ (Phone)*", placeholder="ឧទាហរណ៍: 012 345 678")

        st.subheader("2. ជ្រើសរើសសេវាកម្ម & ជាង")
        s_col1, s_col2 = st.columns(2)
        service = s_col1.selectbox("ជ្រើសរើសសេវាកម្ម*", [
            "ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ ($15.00)",
            "ម៉ាសស្កាតបញ្ចូលវីតាមីន Baby Glow ($15.00)",
            "ញេចសម្អាតគ្រាប់មុន ជម្រុះកោសិកា ($7.50)",
            "បាញ់ Laser ក្លៀក ($5.00)"
        ])
        staff = s_col2.selectbox("ជ្រើសរើសជាង/បុគ្គលិក*", [
            "អ្នកគ្រូ ឡែន (Senior Specialist)",
            "កញ្ញា ម៉ារី",
            "ចៃដន្យ (Any Available)"
        ])

        st.subheader("3. កាលបរិច្ឆេទ & ម៉ោងណាត់")
        d_col1, d_col2 = st.columns(2)
        book_date = d_col1.date_input("ថ្ងៃណាត់ជួប (Date)", datetime.now())
        book_time = d_col2.selectbox("ម៉ោងណាត់ជួប (Time Slot)", [
            "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", 
            "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"
        ])

        note = st.text_area("ចំណាំបន្ថែម (Optional)", placeholder="បញ្ជាក់បន្ថែម ប្រសិនបើមាន...")

        submit_btn = st.form_submit_button("✅ បញ្ជាក់ការកក់ម៉ោង (Confirm Booking)", type="primary", use_container_width=True)

        if submit_btn:
            if not cust_name.strip() or not cust_phone.strip():
                st.error("❌ សូមបញ្ចូលឈ្មោះ និង លេខទូរស័ព្ទឲ្យបានត្រឹមត្រូវ!")
            else:
                # រៀបចំទិន្នន័យផ្ញើទៅ Apps Script
                payload = {
                    "customer_name": cust_name.strip(),
                    "phone": cust_phone.strip(),
                    "service": service,
                    "staff": staff,
                    "date": str(book_date),
                    "time": book_time,
                    "note": note.strip()
                }

                try:
                    # ផ្ញើ Request ទៅ Google Apps Script
                    response = requests.post(APPS_SCRIPT_URL, json=payload)
                    
                    if response.status_code == 200:
                        st.balloons()
                        st.success(f"🎉 អរគុណ {cust_name}! ការកក់ម៉ោងរបស់អ្នកនៅថ្ងៃទី {book_date} វេលាម៉ោង {book_time} ទទួលបានជោគជ័យ។")
                    else:
                        st.error("មានបញ្ហាក្នុងការផ្ញើតិន្នន័យ សូមព្យាយាមម្តងទៀត!")
                except Exception as e:
                    st.error(f"Error: {e}")

elif selected_menu == "📋 បញ្ជីកក់ម៉ោង (Manage Bookings)":
    st.title("📋 បញ្ជីកក់ម៉ោង (Admin)")
    st.info("ដើម្បីមើលទិន្នន័យកក់ សូមបើកមើលក្នុង Google Sheet របស់អ្នកដោយផ្ទាល់។")
