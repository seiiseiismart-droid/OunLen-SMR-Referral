import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Booking App",
    page_icon="💇‍♀️",
    layout="centered"
)

# ----------------------------------------------------------------
# 2. Google Apps Script Web App URL
# ----------------------------------------------------------------
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwlwyd3zHFO-9EzByegad9As7ti6KgwN-dLuZJl-219t6Ez97jpC_wjWMhpUkmWtGhw/exec"

# ----------------------------------------------------------------
# 3. Custom CSS សម្រាប់ធ្វើអោយ UI ដូច Mobile App ក្នុងរូប
# ----------------------------------------------------------------
st.markdown("""
<style>
    /* កំណត់ Background សរុប */
    .main {
        background-color: #f4f6f9;
    }
    
    /* Header Container ពណ៌ក្រមៅរចនាបថ App */
    .app-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 24px 20px;
        border-radius: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    .app-header h2 {
        color: #ffffff !important;
        margin-bottom: 5px;
        font-weight: 700;
    }
    .app-header p {
        color: #94a3b8;
        font-size: 14px;
        margin: 0;
    }

    /* Card Styling សម្រាប់ទម្រង់កក់ */
    .card-box {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 16px;
        border: 1px solid #e2e8f0;
    }
    
    .card-title {
        font-weight: 600;
        font-size: 16px;
        color: #1e293b;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Styling សម្រាប់ Service Option Cards */
    .service-card {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .service-price {
        background-color: #2563eb;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 13px;
    }

    /* កែសម្រួលប៊ូតុង Submit */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 12px;
        font-size: 16px;
        border: none;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #dc2626 0%, #b91c1c 100%);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 4. Navigation (Mode Selection)
# ----------------------------------------------------------------
is_client_view = st.query_params.get("mode") == "client"

if not is_client_view:
    selected_menu = st.radio(
        "📌 Menu",
        ["📅 កក់ម៉ោងថ្មី (Booking)", "📋 បញ្ជីកក់ម៉ោង (Manage)"],
        horizontal=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
else:
    selected_menu = "📅 កក់ម៉ោងថ្មី (Booking)"

# ----------------------------------------------------------------
# 5. CLIENT BOOKING FORM (ទម្រង់ UI App)
# ----------------------------------------------------------------
if selected_menu == "📅 កក់ម៉ោងថ្មី (Booking)":
    
    # 📱 Top Header (ដូចស្ទីល App ក្នុងរូប)
    st.markdown("""
        <div class="app-header">
            <h2>💇‍♀️ អូនឡែន សម្រស់</h2>
            <p>ប្រព័ន្ធកក់ម៉ោងសេវាកម្មរហ័ស & ងាយស្រួល</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("booking_form", clear_on_submit=True):
        
        # 👤 1. ព័ត៌មានអតិថិជន
        st.markdown('<div class="card-title">👤 ព័ត៌មានអតិថិជន (Customer Info)</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        cust_name = c1.text_input("ឈ្មោះអតិថិជន*", placeholder="ឧ. អ្នកស្រី គឹម")
        cust_phone = c2.text_input("លេខទូរស័ព្ទ*", placeholder="ឧ. 012 345 678")

        st.markdown("<hr style='margin: 15px 0; border-color: #f1f5f9;'>", unsafe_allow_html=True)

        # 💅 2. ជ្រើសរើសសេវាកម្ម & ជាង
        st.markdown('<div class="card-title">✨ ជ្រើសរើសសេវាកម្ម & ជាង</div>', unsafe_allow_html=True)
        s_col1, s_col2 = st.columns(2)
        service = s_col1.selectbox("សេវាកម្ម*", [
            "ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ ($15.00)",
            "ម៉ាសស្កាតបញ្ចូលវីតាមីន Baby Glow ($15.00)",
            "ញេចសម្អាតគ្រាប់មុន ជម្រុះកោសិកា ($7.50)",
            "បាញ់ Laser ក្លៀក ($5.00)"
        ])
        staff = s_col2.selectbox("ជាង/បុគ្គលិក*", [
            "អ្នកគ្រូ ឡែន (Senior Specialist)",
            "កញ្ញា ម៉ារី",
            "ចៃដន្យ (Any Available)"
        ])

        st.markdown("<hr style='margin: 15px 0; border-color: #f1f5f9;'>", unsafe_allow_html=True)

        # 📅 3. កាលបរិច្ឆេទ & ម៉ោងណាត់
        st.markdown('<div class="card-title">⏰ កាលបរិច្ឆេទ & ម៉ោងណាត់</div>', unsafe_allow_html=True)
        d_col1, d_col2 = st.columns(2)
        book_date = d_col1.date_input("ថ្ងៃណាត់ជួប", datetime.now())
        book_time = d_col2.selectbox("ម៉ោងណាត់ជួប", [
            "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", 
            "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"
        ])

        note = st.text_area("ចំណាំបន្ថែម (Optional)", placeholder="បញ្ជាក់បន្ថែម...")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 🔴 ប៊ូតុង Confirm
        submit_btn = st.form_submit_button("✅ បញ្ជាក់ការកក់ម៉ោង (Confirm Booking)", use_container_width=True)

        if submit_btn:
            if not cust_name.strip() or not cust_phone.strip():
                st.error("❌ សូមបញ្ចូលឈ្មោះ និង លេខទូរស័ព្ទឲ្យបានត្រឹមត្រូវ!")
            else:
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
                    response = requests.post(APPS_SCRIPT_URL, json=payload, allow_redirects=True)
                    if response.status_code in [200, 302]:
                        st.balloons()
                        st.success(f"🎉 អរគុណ {cust_name}! ការកក់ម៉ោងនៅថ្ងៃទី {book_date} វេលាម៉ោង {book_time} ទទួលបានជោគជ័យ។")
                    else:
                        st.error(f"មានបញ្ហាក្នុងការផ្ញើតិន្នន័យ (Code: {response.status_code})")
                except Exception as e:
                    st.error(f"Error: {e}")

    # 🏷️ បង្ហាញបញ្ជីសេវាកម្មពេញនិយម (Style ដូច Card បង្ហាញជើងហោះហើរក្នុងរូប)
    st.markdown("<br><h4>🔥 សេវាកម្មពេញនិយម</h4>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="service-card">
            <div>
                <strong>💆‍♀️ ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ</strong><br>
                <small style="color: #64748b;">ថែទាំស្បែកមុខអោយភ្លឺថ្លា</small>
            </div>
            <div class="service-price">$15.00</div>
        </div>
        <div class="service-card">
            <div>
                <strong>✨ ម៉ាសស្កាត Baby Glow</strong><br>
                <small style="color: #64748b;">ផ្ដល់សំណើម និងជម្រុះកោសិកា</small>
            </div>
            <div class="service-price">$15.00</div>
        </div>
        <div class="service-card">
            <div>
                <strong>🎯 ញេចសម្អាតគ្រាប់មុន</strong><br>
                <small style="color: #64748b;">សម្អាតស្បែកមុខជម្រៅជ្រៅ</small>
            </div>
            <div class="service-price">$7.50</div>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# 6. ADMIN MANAGE BOOKINGS
# ----------------------------------------------------------------
elif selected_menu == "📋 បញ្ជីកក់ម៉ោង (Manage)":
    st.title("📋 បញ្ជីកក់ម៉ោង (Admin Dashboard)")
    
    col_t, col_b = st.columns([4, 1])
    with col_b:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    try:
        res = requests.get(APPS_SCRIPT_URL, allow_redirects=True)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("មិនទាន់មានទិន្នន័យកក់នៅឡើយទេ។")
        else:
            st.error("មិនអាចទាញយកទិន្នន័យបានទេ!")
    except Exception as e:
        st.error(f"Error: {e}")
