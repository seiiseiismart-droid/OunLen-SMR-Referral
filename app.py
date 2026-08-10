import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time

# ----------------------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - System",
    page_icon="💇‍♀️",
    layout="wide"
)

# ----------------------------------------------------------------
# 2. Google Apps Script Web App URL
# ----------------------------------------------------------------
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwlwyd3zHFO-9EzByegad9As7ti6KgwN-dLuZJl-219t6Ez97jpC_wjWMhpUkmWtGhw/exec"

# ----------------------------------------------------------------
# 3. Custom CSS
# ----------------------------------------------------------------
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    
    /* Header Container */
    .app-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white; 
        padding: 20px; 
        border-radius: 16px; 
        margin-bottom: 20px;
    }
    
    /* Service Card Design */
    .service-card {
        background: #1e293b; 
        border: 1px solid #334155; 
        border-radius: 12px;
        padding: 12px 16px; 
        margin-bottom: 8px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        color: white;
    }
    .service-price { 
        background-color: #2563eb; 
        color: white; 
        padding: 4px 12px; 
        border-radius: 20px; 
        font-weight: bold; 
    }

    /* ពង្រីកអក្សរក្នុងតារាង DataFrame */
    div[data-testid="stDataFrame"] * {
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# Helper Functions សម្រាប់ Format កាលបរិច្ឆេទ & ម៉ោង ឲ្យស្អាត
# ----------------------------------------------------------------
def format_clean_date(date_str):
    if not date_str:
        return "-"
    d_str = str(date_str)
    if "T" in d_str:
        d_str = d_str.split("T")[0]
    return d_str

def format_clean_time(time_str):
    if not time_str:
        return "-"
    t_str = str(time_str)
    # ប្រសិនបើទិន្នន័យជាប់ ISO Format ដូចជា 1899-12-30T01:17:56.000Z
    if "T" in t_str:
        try:
            time_part = t_str.split("T")[1].split(".")[0]
            dt = datetime.strptime(time_part, "%H:%M:%S")
            return dt.strftime("%I:%M %p")
        except Exception:
            return t_str.split("T")[0]
    return t_str

# ----------------------------------------------------------------
# 4. Data Loading
# ----------------------------------------------------------------
@st.cache_data(ttl=3)
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
        s_name = str(row[0])
        try:
            s_price = float(row[1])
        except (ValueError, TypeError):
            s_price = 0.0
        
        s_text = f"{s_name} (${s_price:.2f})"
        services_list.append(s_text)
        services_dict[s_name] = s_price

# ----------------------------------------------------------------
# 5. Route Mode Detection
# ----------------------------------------------------------------
mode = st.query_params.get("mode")

# =================================================================
# 📱 1. CLIENT DASHBOARD (?mode=client)
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

        # slots 08:00 AM - 09:30 PM
        all_slots = []
        for h in range(8, 22):
            for m in (0, 30):
                if h == 21 and m == 30:
                    all_slots.append("09:30 PM")
                    break
                elif h < 22:
                    t_obj = time(h, m)
                    all_slots.append(t_obj.strftime("%I:%M %p"))

        booked_slots = []
        if len(data.get("bookings", [])) > 1:
            for b in data["bookings"][1:]:
                if len(b) >= 7 and format_clean_date(b[5]) == str(book_date):
                    booked_slots.append(format_clean_time(b[6]))

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

    st.markdown("<br><h4>🔥 បញ្ជីសេវាកម្ម និងតម្លៃ</h4>", unsafe_allow_html=True)
    if len(data.get("services", [])) > 1:
        for s in data["services"][1:]:
            try:
                p = float(s[1])
            except (ValueError, TypeError):
                p = 0.0
            st.markdown(f"""
                <div class="service-card">
                    <div><strong>{s[0]}</strong><br><small style="color:#94a3b8;">{s[2] if len(s)>2 else ''}</small></div>
                    <div class="service-price">${p:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# =================================================================
# 👑 2. ADMIN DASHBOARD (?mode=admin)
# =================================================================
elif mode == "admin":
    st.title("👑 Admin Dashboard (ម្ចាស់ហាង)")
    
    tab1, tab2 = st.tabs(["📋 បញ្ជីកក់ម៉ោងអតិថិជន", "⚙️ គ្រប់គ្រងសេវាកម្ម & តម្លៃ"])

    # Tab 1: បញ្ជីកក់ម៉ោង
    with tab1:
        st.subheader("📋 បញ្ជីការកក់ទាំងអស់")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        bookings_raw = data.get("bookings", [])
        if len(bookings_raw) > 1:
            headers = bookings_raw[0]
            df_b = pd.DataFrame(bookings_raw[1:], columns=headers)
            
            # Format កាលបរិច្ឆេទ និងម៉ោង ឲ្យស្អាត
            if len(headers) >= 7:
                df_b[headers[5]] = df_b[headers[5]].apply(format_clean_date)
                df_b[headers[6]] = df_b[headers[6]].apply(format_clean_time)

            # 1. បង្ហាញក្នុង Table
            st.dataframe(
                df_b,
                use_container_width=True,
                hide_index=True,
                height=350,
                column_config={
                    headers[0]: st.column_config.TextColumn("⏰ ពេលវេលាកក់", width="medium"),
                    headers[1]: st.column_config.TextColumn("👤 ឈ្មោះអតិថិជន", width="medium"),
                    headers[2]: st.column_config.TextColumn("📞 លេខទូរស័ព្ទ", width="small"),
                    headers[3]: st.column_config.TextColumn("💆‍♀️ សេវាកម្ម", width="large"),
                    headers[4]: st.column_config.TextColumn("👩‍ស្ប៉ា ជាង/បុគ្គលិក", width="medium"),
                    headers[5]: st.column_config.TextColumn("📅 ថ្ងៃណាត់", width="small"),
                    headers[6]: st.column_config.TextColumn("🕒 ម៉ោងណាត់", width="small"),
                    headers[7]: st.column_config.TextColumn("📝 ចំណាំ", width="medium"),
                }
            )

            # 2. បង្ហាញជា Card ស្អាតច្បាស់ៗ
            st.markdown("---")
            st.subheader("📱 មើលជាទម្រង់ Card (ងាយស្រួលមើលលើទូរស័ព្ទ)")
            for idx, row in df_b.iterrows():
                clean_date = format_clean_date(row.get(headers[5], ''))
                clean_time = format_clean_time(row.get(headers[6], ''))
                note_text = row.get(headers[7], '')
                note_display = note_text if note_text and str(note_text).strip() != "" else "-"

                st.markdown(f"""
                <div style="background-color:#1e293b; padding:16px; border-radius:12px; margin-bottom:12px; border-left:6px solid #2563eb; color:white; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#60a5fa;">👤 {row.get(headers[1], '')}</h3>
                        <span style="background-color:#059669; color:white; padding:3px 10px; border-radius:12px; font-weight:bold; font-size:14px;">📞 {row.get(headers[2], '')}</span>
                    </div>
                    <p style="margin:8px 0 4px 0; font-size:16px; color:#f1f5f9;"><b>💆‍♀️ សេវាកម្ម:</b> {row.get(headers[3], '')}</p>
                    <p style="margin:4px 0; font-size:15px; color:#cbd5e1;">
                        <b>📅 ថ្ងៃណាត់:</b> <span style="color:#38bdf8; font-weight:bold;">{clean_date}</span> | 
                        <b>🕒 ម៉ោង:</b> <span style="color:#f59e0b; font-weight:bold;">{clean_time}</span> | 
                        <b>👩‍ស្ប៉ា ជាង:</b> {row.get(headers[4], '')}
                    </p>
                    <p style="margin:4px 0 0 0; font-size:14px; color:#94a3b8;"><b>📝 ចំណាំ:</b> {note_display}</p>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info("មិនទាន់មានទិន្នន័យកក់នៅឡើយទេ។")

    # Tab 2: គ្រប់គ្រងសេវាកម្ម
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
            updated_price = st.number_input("តម្លៃថ្មី ($)", value=float(current_price), min_value=0.0, step=0.5)

            if st.button("💾 រក្សាទុកតម្លៃថ្មី"):
                payload = {
                    "action": "update_service",
                    "service_name": selected_s_edit,
                    "price": updated_price
                }
                requests.post(APPS_SCRIPT_URL, json=payload, allow_redirects=True)
                st.success(f"✅ បានកែប្រែតម្លៃសេវាកម្ម '{selected_s_edit}' ទៅជា ${updated_price:.2f} ជោគជ័យ!")
                st.cache_data.clear()
