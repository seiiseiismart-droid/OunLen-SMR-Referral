import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time

# 1. Page Config
st.set_page_config(page_title="OunLen SMR - System", page_icon="💇‍♀️", layout="centered")

# 2. Apps Script URL
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwlwyd3zHFO-9EzByegad9As7ti6KgwN-dLuZJl-219t6Ez97jpC_wjWMhpUkmWtGhw/exec"

# 3. Custom CSS Style
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .app-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white; padding: 20px; border-radius: 16px; margin-bottom: 20px;
    }
    .service-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;
    }
    .service-price { background-color: #2563eb; color: white; padding: 4px 10px; border-radius: 20px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 4. Fetch Data Function
@st.cache_data(ttl=5)
def load_data():
    try:
        res = requests.get(APPS_SCRIPT_URL, allow_redirects=True)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"bookings": [], "services": []}

data = load_data()

# Process Services List
services_list = []
services_dict = {}
if len(data.get("services", [])) > 1:
    for row in data["services"][1:]:
        s_name, s_price = str(row[0]), row[1]
        s_text = f"{s_name} (${float(s_price):.2f})"
        services_list.append(s_text)
        services_dict[s_name] = float(s_price)

# Mode Detection
mode = st.query_params.get("mode")

# =================================================================
# 📱 DASHBOARD 1: អតិថិជន (Client View) - URL: ?mode=client
# =================================================================
if mode == "client" or mode is None:
    st.markdown("""
        <div class="app-header">
            <h2 style="color:white; margin:0;">💇‍♀️ អូនឡែន សម្រស់</h2>
            <p style="color:#94a3b8; margin:0;">ប្រព័ន្ធកក់ម៉ោងសេវាកម្មអនឡាញ</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("booking_form", clear_on_submit=True):
        st.subheader("👤 1. ព័ត៌មានអតិថិជន")
        c1, c2 = st.columns(2)
        cust_name = c1.text_input("ឈ្មោះអតិថិជន*")
        cust_phone = c2.text_input("លេខទូរស័ព្ទ*")

        st.subheader("✨ 2. ជ្រើសរើសសេវាកម្ម & ជាង")
        s_col1, s_col2 = st.columns(2)
        service = s_col1.selectbox("សេវាកម្ម*", services_list if services_list else ["គ្មានសេវាកម្ម"])
        staff = s_col2.selectbox("ជាង/បុគ្គលិក*", ["អ្នកគ្រូ ឡែន", "កញ្ញា ម៉ារី", "ចៃដន្យ (Any)"])

        st.subheader("⏰ 3. កាលបរិច្ឆេទ & ម៉ោងណាត់")
        d_col1, d_col2 = st.columns(2)
        book_date = d_col1.date_input("ថ្ងៃណាត់ជួប", datetime.now())

        # GENERATE TIME SLOTS (08:00 AM - 09:30 PM)
        all_slots = []
        for h in range(8, 22):
            for m in (0, 30):
                if h == 21 and m == 30:
                    all_slots.append("09:30 PM")
                    break
                elif h < 22:
                    t_obj = time(h, m)
                    all_slots.append(t_obj.strftime("%I:%M %p"))

        # FILTER OUT BOOKED SLOTS
        booked_slots = []
        if len(data.get("bookings", [])) > 1:
            for b in data["bookings"][1:]:
                if len(b) >= 7 and str(b[5]) == str(book_date):
                    booked_slots.append(str(b[6]))

        available_slots = [slot for slot in all_slots if slot not in booked_slots]

        if available_slots:
            book_time = d_col2.selectbox("ម៉ោងណាត់ជួប (បង្ហាញតែម៉ោងទំនេរ)", available_slots)
        else:
            d_col2.warning("❌ ថ្ងៃនេះពេញម៉ោងអស់ហើយ!")
            book_time = None

        note = st.text_area("ចំណាំបន្ថែម (Optional)")
        submit_btn = st.form_submit_button("✅ បញ្ជាក់ការកក់ម៉ោង (Confirm)", type="primary", use_container_width=True)

        if submit_btn:
            if not cust_name.strip() or not cust_phone.strip():
                st.error("❌ សូមបញ្ចូលឈ្មោះ និង លេខទូរស័ព្ទ!")
            elif not book_time:
                st.error("❌ សូមជ្រើសរើសថ្ងៃផ្សេង ព្រោះថ្ងៃនេះអស់ម៉ោងទំនេរហើយ!")
            else:
                payload = {
                    "action": "add_booking",
                    "customer_name": cust_name.strip(),
                    "phone": cust_phone.strip(),
                    "service": service,
                    "staff": staff,
                    "date": str(book_date),
                    "time": book_time,
                    "note": note.strip()
                }
                res = requests.post(APPS_SCRIPT_URL, json=payload, allow_redirects=True)
                if res.status_code in [200, 302]:
                    st.balloons()
                    st.success(f"🎉 អរគុណ {cust_name}! បានកក់ម៉ោង {book_time} នៅថ្ងៃ {book_date} ជោគជ័យ។")
                    st.cache_data.clear()
                else:
                    st.error("មានបញ្ហាក្នុងការផ្ញើតិន្នន័យ!")

    # Display Services List
    st.markdown("<br><h4>🔥 បញ្ជីសេវាកម្ម និងតម្លៃ</h4>", unsafe_allow_html=True)
    if len(data.get("services", [])) > 1:
        for s in data["services"][1:]:
            st.markdown(f"""
                <div class="service-card">
                    <div><strong>{s[0]}</strong><br><small style="color:#64748b;">{s[2] if len(s)>2 else ''}</small></div>
                    <div class="service-price">${float(s[1]):.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# =================================================================
# 👑 DASHBOARD 2: ម្ចាស់ហាង (Admin View) - URL: ?mode=admin
# =================================================================
elif mode == "admin":
    st.title("👑 Admin Dashboard (ម្ចាស់ហាង)")
    
    tab1, tab2 = st.tabs(["📋 បញ្ជីកក់ម៉ោងអតិថិជន", "⚙️ គ្រប់គ្រងសេវាកម្ម & តម្លៃ"])

    # Tab 1: Bookings List
    with tab1:
        st.subheader("📋 បញ្ជីការកក់ទាំងអស់")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        if len(data.get("bookings", [])) > 1:
            df_b = pd.DataFrame(data["bookings"][1:], columns=data["bookings"][0])
            st.dataframe(df_b, use_container_width=True)
        else:
            st.info("មិនទាន់មានទិន្នន័យកក់នៅឡើយទេ។")

    # Tab 2: Service & Price Management
    with tab2:
        st.subheader("➕ បន្ថែមសេវាកម្មថ្មី")
        with st.form("add_service_form", clear_on_submit=True):
            new_s_name = st.text_input("ឈ្មោះសេវាកម្ម*")
            new_s_price = st.number_input("តម្លៃ ($)*", min_value=0.0, step=0.5)
            new_s_desc = st.text_input("ការពិពណ៌នា (Optional)")
            btn_add_s = st.form_submit_button("➕ បន្ថែមសេវាកម្ម")

            if btn_add_s and new_s_name.strip():
                payload = {
                    "action": "add_service",
                    "service_name": new_s_name.strip(),
                    "price": new_s_price,
                    "description": new_s_desc.strip()
                }
                requests.post(APPS_SCRIPT_URL, json=payload, allow_redirects=True)
                st.success("✅ បានបន្ថែមសេវាកម្មថ្មីជោគជ័យ!")
                st.cache_data.clear()

        st.markdown("---")
        st.subheader("✏️ កែប្រែតម្លៃសេវាកម្មដែលមានស្រាប់")
        if services_dict:
            selected_s_edit = st.selectbox("ជ្រើសរើសសេវាកម្មត្រូវកែតម្លៃ", list(services_dict.keys()))
            current_price = services_dict[selected_s_edit]
            updated_price = st.number_input("តម្លៃថ្មី ($)", value=current_price, min_value=0.0, step=0.5)

            if st.button("💾 រក្សាទុកតម្លៃថ្មី"):
                payload = {
                    "action": "update_service",
                    "service_name": selected_s_edit,
                    "price": updated_price
                }
                requests.post(APPS_SCRIPT_URL, json=payload, allow_redirects=True)
                st.success(f"✅ បានកែប្រែតម្លៃសេវាកម្ម '{selected_s_edit}' ទៅជា ${updated_price:.2f} ជោគជ័យ!")
                st.cache_data.clear()
