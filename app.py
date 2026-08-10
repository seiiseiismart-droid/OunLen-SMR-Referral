import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - System Booking",
    page_icon="📅",
    layout="wide"
)

# ----------------------------------------------------------------
# 2. Connect to Google Sheets
# ----------------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def get_booking_data():
    """ទាញយកទិន្នន័យពី Google Sheets"""
    try:
        data = conn.read(ttl="0") # ttl="0" ដើម្បីឲ្យវាទាញទិន្នន័យថ្មីជានិច្ច
        return data
    except Exception:
        return pd.DataFrame(columns=[
            "Timestamp", "Customer_Name", "Phone", "Service", "Staff", "Date", "Time", "Note", "Status"
        ])

# ----------------------------------------------------------------
# 3. Mode Switching (Admin vs Client View)
# ----------------------------------------------------------------
is_client_view = st.query_params.get("mode") == "client"

if is_client_view:
    # សម្រាប់អតិថិជន៖ មិនបង្ហាញ Menu អ្វីទាំងអស់
    selected_menu = "📅 កក់ម៉ោងថ្មី (New Booking)"
else:
    # សម្រាប់ Admin/Staff៖ មាន Menu គ្រប់គ្រង
    selected_menu = st.radio(
        "📌 Navigation Menu",
        [
            "📅 កក់ម៉ោងថ្មី (New Booking)",
            "📋 បញ្ជីកក់ម៉ោងទាំងអស់ (Manage Bookings)",
            "📊 របាយការណ៍ (Report)"
        ],
        horizontal=True
    )
    st.markdown("---")

# ----------------------------------------------------------------
# 4. CUSTOMER BOOKING FORM
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
                # ទាញយកទិន្នន័យចាស់
                existing_df = get_booking_data()

                # បង្កើត Row ថ្មី
                new_data = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Customer_Name": cust_name.strip(),
                    "Phone": cust_phone.strip(),
                    "Service": service,
                    "Staff": staff,
                    "Date": str(book_date),
                    "Time": book_time,
                    "Note": note.strip(),
                    "Status": "Pending"
                }])

                # បញ្ចូល Row ថ្មីទៅក្នុង DataFrame
                updated_df = pd.concat([existing_df, new_data], ignore_index=True)

                # រក្សាទុកចូល Google Sheets វិញ
                conn.update(data=updated_df)

                st.balloons()
                st.success(f"🎉 អរគុណ {cust_name}! ការកក់ម៉ោងរបស់អ្នកនៅថ្ងៃទី {book_date} វេលាម៉ោង {book_time} ទទួលបានជោគជ័យ។")

# ----------------------------------------------------------------
# 5. ADMIN MANAGE BOOKINGS
# ----------------------------------------------------------------
elif selected_menu == "📋 បញ្ជីកក់ម៉ោងទាំងអស់ (Manage Bookings)":
    st.title("📋 បញ្ជីការកក់ម៉ោងរបស់អតិថិជន (Admin Dashboard)")
    
    if st.button("🔄 ធ្វើបច្ចុប្បន្នភាពទិន្នន័យ (Refresh)"):
        st.rerun()

    df = get_booking_data()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("មិនទាន់មានទិន្នន័យកក់នៅឡើយទេ។")

elif selected_menu == "📊 របាយការណ៍ (Report)":
    st.title("📊 របាយការណ៍សង្ខេប")
    df = get_booking_data()
    st.metric("ចំនួនអតិថិជនកក់សរុប", f"{len(df)} នាក់")
