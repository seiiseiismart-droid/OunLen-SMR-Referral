import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, time

# ----------------------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Advanced System",
    page_icon="💇‍♀️",
    layout="wide"
)

# ----------------------------------------------------------------
# 2. Configuration & Secrets
# ----------------------------------------------------------------
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwlwyd3zHFO-9EzByegad9As7ti6KgwN-dLuZJl-219t6Ez97jpC_wjWMhpUkmWtGhw/exec"

TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", "8802043451:AAEAp35949z9IQLa5kj6Ecl75Q5uzIv-F_4")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "-1004491712284")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "123456")

# ----------------------------------------------------------------
# 3. Helper Functions
# ----------------------------------------------------------------
def send_telegram_message(name, phone, services_str, staff, date_str, time_str, total_price, note, status="Pending"):
    """ផ្ញើសារជូនដំណឹងចូល Telegram Group"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        status_emoji = {"Pending": "🟡", "Confirmed": "🟢", "Completed": "🔵", "Cancelled": "🔴"}.get(status, "🔔")
        message = (
            f"{status_emoji} *ការកក់ម៉ោង ({status})*\n\n"
            f"👤 *អតិថិជន:* {name}\n"
            f"📞 *លេខទូរស័ព្ទ:* `{phone}`\n"
            f"💆‍♀️ *សេវាកម្ម:* {services_str}\n"
            f"💰 *តម្លៃសរុប:* ${total_price:.2f}\n"
            f"👩‍ស្ប៉ា *ជាង/បុគ្គលិក:* {staff}\n"
            f"📅 *ថ្ងៃណាត់:* {date_str}\n"
            f"🕒 *ម៉ោងណាត់:* {time_str}\n"
            f"📝 *ចំណាំ:* {note if note else '-'}"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
        except Exception:
            pass

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
    if "T" in t_str:
        try:
            time_part = t_str.split("T")[1].split(".")[0]
            dt = datetime.strptime(time_part, "%H:%M:%S")
            return dt.strftime("%I:%M %p")
        except Exception:
            return t_str.split("T")[0]
    return t_str

# ----------------------------------------------------------------
# 4. Custom CSS
# ----------------------------------------------------------------
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    .app-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white; padding: 20px; border-radius: 16px; margin-bottom: 20px;
    }
    .service-card {
        background: #1e293b; border: 1px solid #334155; border-radius: 12px;
        padding: 12px 16px; margin-bottom: 8px; display: flex; 
        justify-content: space-between; align-items: center; color: white;
    }
    .service-price { background-color: #2563eb; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
    .status-badge { padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; color: white; }
    .bg-pending { background-color: #d97706; }
    .bg-confirmed { background-color: #059669; }
    .bg-completed { background-color: #2563eb; }
    .bg-cancelled { background-color: #dc2626; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 5. Data Loading & Parsing
# ----------------------------------------------------------------
@st.cache_data(ttl=3)
def load_data():
    try:
        res = requests.get(APPS_SCRIPT_URL, allow_redirects=True, timeout=8)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"bookings": [], "services": [], "blocked_dates": []}

data = load_data()

# Process Services List & Dict
services_dict = {}
if len(data.get("services", [])) > 1:
    for row in data["services"][1:]:
        s_name = str(row[0])
        try:
            s_price = float(row[1])
        except (ValueError, TypeError):
            s_price = 0.0
        services_dict[s_name] = s_price

# Process Blocked Dates
blocked_dates_dict = {}
blocked_dates_list = []
if len(data.get("blocked_dates", [])) > 1:
    for idx, row in enumerate(data["blocked_dates"][1:]):
        b_date = format_clean_date(row[0])
        b_reason = row[1] if len(row) > 1 else "ថ្ងៃសម្រាក"
        blocked_dates_dict[b_date] = b_reason
        blocked_dates_list.append({"row_index": idx + 2, "date": b_date, "reason": b_reason})

# Process Bookings DataFrame
bookings_raw = data.get("bookings", [])
df_bookings = pd.DataFrame()

if len(bookings_raw) > 1:
    rows = []
    for idx, r in enumerate(bookings_raw[1:]):
        row = list(r) + [""] * (11 - len(r))
        c_date = format_clean_date(row[5])
        c_time = format_clean_time(row[6])
        status = str(row[8]).strip() if row[8] else "Pending"
        try:
            price = float(row[9]) if row[9] != "" else 0.0
        except Exception:
            price = 0.0
            
        rows.append({
            "sheet_row": idx + 2,
            "Created At": row[0],
            "Customer Name": str(row[1]),
            "Phone": str(row[2]),
            "Services": str(row[3]),
            "Staff": str(row[4]),
            "Date": c_date,
            "Time": c_time,
            "Note": str(row[7]),
            "Status": status,
            "Total Price": price,
            "Deposit": str(row[10])
        })
    df_bookings = pd.DataFrame(rows)

# ----------------------------------------------------------------
# 6. Route Mode Detection
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

    tab_client1, tab_client2 = st.tabs(["📝 កក់ម៉ោង (Book Now)", "🔍 ពិនិត្យមើលការកក់ (Check Booking)"])

    # Tab 1: ផ្ទាំងកក់ម៉ោង
    with tab_client1:
        with st.form("booking_form", clear_on_submit=True):
            st.subheader("👤 1. ព័ត៌មានអតិថិជន")
            c1, c2 = st.columns(2)
            cust_name = c1.text_input("ឈ្មោះអតិថិជន*")
            cust_phone = c2.text_input("លេខទូរស័ព្ទ*")

            st.subheader("✨ 2. ជ្រើសរើសសេវាកម្ម (អាចជ្រើសបានច្រើន) & ជាង")
            s_col1, s_col2 = st.columns(2)
            
            selected_services = s_col1.multiselect(
                "ជ្រើសរើសសេវាកម្ម*", 
                options=list(services_dict.keys()),
                default=[list(services_dict.keys())[0]] if services_dict else []
            )
            
            total_calc_price = sum(services_dict.get(s, 0.0) for s in selected_services)
            s_col1.info(f"💵 តម្លៃសរុបប៉ាន់ស្មាន: **${total_calc_price:.2f}**")

            staff = s_col2.selectbox("ជាង/បុគ្គលិក*", ["អ្នកគ្រូ ឡែន", "កញ្ញា ម៉ារី", "ចៃដន្យ (Any)"])

            st.subheader("⏰ 3. កាលបរិច្ឆេទ & ម៉ោងណាត់")
            d_col1, d_col2 = st.columns(2)
            book_date = d_col1.date_input("ថ្ងៃណាត់ជួប", datetime.now())
            book_date_str = str(book_date)

            is_blocked = book_date_str in blocked_dates_dict

            # រៀបចំ Time Slots 08:00 AM - 09:30 PM
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
            if not df_bookings.empty:
                active_b = df_bookings[(df_bookings["Date"] == book_date_str) & (df_bookings["Status"] != "Cancelled")]
                booked_slots = active_b["Time"].tolist()

            available_slots = [slot for slot in all_slots if slot not in booked_slots]

            if is_blocked:
                d_col2.error(f"❌ ថ្ងៃនេះហាងបិទសម្រាក ({blocked_dates_dict[book_date_str]})")
                book_time = None
            elif available_slots:
                book_time = d_col2.selectbox("ម៉ោងណាត់ជួប (បង្ហាញតែម៉ោងទំនេរ)", available_slots)
            else:
                d_col2.warning("❌ ថ្ងៃនេះពេញម៉ោងអស់ហើយ!")
                book_time = None

            note = st.text_area("ចំណាំបន្ថែម (Optional)")

            st.markdown("---")
            st.subheader("💳 4. ការវេរប្រាក់កក់ (ABA KHQR Deposit)")
            st.info("💡 ដើម្បីធានាកក់ម៉ោងបានជោគជ័យ សូមវេរប្រាក់កក់ $2.00 មកកាន់ ABA: **000 123 456 (OunLen Salon)**")
            deposit_ref = st.text_input("លេខទ្រនុង / ឈ្មោះគណនីវេរប្រាក់កក់ (Optional)")

            submit_btn = st.form_submit_button("✅ បញ្ជាក់ការកក់ម៉ោង (Confirm)", type="primary", use_container_width=True)

            if submit_btn:
                if not cust_name.strip() or not cust_phone.strip():
                    st.error("❌ សូមបញ្ចូលឈ្មោះ និង លេខទូរស័ព្ទ!")
                elif not selected_services:
                    st.error("❌ សូមជ្រើសរើសសេវាកម្មយ៉ាងហោចណាស់ 1!")
                elif is_blocked:
                    st.error("❌ មិនអាចកក់បានទេ ព្រោះថ្ងៃនេះហាងបិទសម្រាក!")
                elif not book_time:
                    st.error("❌ សូមជ្រើសរើសថ្ងៃផ្សេង ព្រោះថ្ងៃនេះអស់ម៉ោងទំនេរហើយ!")
                else:
                    services_joined = ", ".join(selected_services)
                    payload = {
                        "action": "add_booking",
                        "customer_name": cust_name.strip(),
                        "phone": cust_phone.strip(),
                        "service": services_joined,
                        "staff": staff,
                        "date": book_date_str,
                        "time": book_time,
                        "note": note.strip(),
                        "status": "Pending",
                        "total_price": total_calc_price,
                        "deposit": deposit_ref.strip() if deposit_ref else "No Deposit Ref"
                    }
                    
                    res = requests.post(APPS_SCRIPT_URL, json=payload, allow_redirects=True, timeout=10)
                    send_telegram_message(cust_name.strip(), cust_phone.strip(), services_joined, staff, book_date_str, book_time, total_calc_price, note.strip(), "Pending")
                    
                    if res.status_code in [200, 302]:
                        st.balloons()
                        st.success(f"🎉 អរគុណ {cust_name}! បានកក់ម៉ោង {book_time} នៅថ្ងៃ {book_date_str} ជោគជ័យ។")
                        st.cache_data.clear()
                    else:
                        st.error("មានបញ្ហាក្នុងការផ្ញើទិន្នន័យ!")

        st.markdown("<br><h4>🔥 បញ្ជីសេវាកម្ម និងតម្លៃ</h4>", unsafe_allow_html=True)
        for s_name, s_price in services_dict.items():
            st.markdown(f"""
                <div class="service-card">
                    <div><strong>{s_name}</strong></div>
                    <div class="service-price">${s_price:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

    # Tab 2: ពិនិត្យមើលការកក់
    with tab_client2:
        st.subheader("🔍 ស្វែងរកការកក់របស់អ្នក")
        search_phone = st.text_input("បញ្ចូលលេខទូរស័ព្ទរបស់អ្នកដើម្បីត្រួតពិនិត្យ:")
        if search_phone.strip():
            if not df_bookings.empty:
                my_b = df_bookings[df_bookings["Phone"].str.contains(search_phone.strip())]
                if not my_b.empty:
                    st.success(f"រកឃើញ {len(my_b)} ការកក់ សម្រាប់លេខ {search_phone}:")
                    for _, row in my_b.iterrows():
                        st.markdown(f"""
                        <div style="background-color:#1e293b; padding:16px; border-radius:12px; margin-bottom:12px; border:1px solid #334155; color:white;">
                            <h4 style="color:#60a5fa; margin:0;">💆‍♀️ សេវាកម្ម: {row['Services']}</h4>
                            <p style="margin:4px 0;"><b>📅 ថ្ងៃណាត់:</b> {row['Date']} | <b>🕒 ម៉ោង:</b> {row['Time']}</p>
                            <p style="margin:4px 0;"><b>💰 តម្លៃសរុប:</b> ${row['Total Price']:.2f} | <b>👩‍ស្ប៉ា ជាង:</b> {row['Staff']}</p>
                            <p style="margin:4px 0;"><b>📌 ស្ថានភាព:</b> <span class="status-badge bg-{row['Status'].lower()}">{row['Status']}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("រកមិនឃើញទិន្នន័យកក់សម្រាប់លេខទូរស័ព្ទនេះទេ។")
            else:
                st.info("មិនទាន់មានទិន្នន័យកក់ឡើយ។")

# =================================================================
# 👑 2. ADMIN DASHBOARD (?mode=admin)
# =================================================================
elif mode == "admin":
    st.title("👑 Admin Dashboard (ម្ចាស់ហាង)")

    # 1. Authentication
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.subheader("🔒 សូមបញ្ចូលពាក្យសម្ងាត់ដើម្បីចូលប្រព័ន្ធ Admin")
        input_pass = st.text_input("ពាក្យសម្ងាត់ Admin", type="password")
        if st.button("🔑 ចូលប្រព័ន្ធ", type="primary"):
            if input_pass == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("❌ ពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ!")
        st.stop()

    col_adm1, col_adm2 = st.columns([6, 1])
    with col_adm2:
        if st.button("🚪 ចាកចេញ"):
            st.session_state.admin_authenticated = False
            st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 គ្រប់គ្រងការកក់", 
        "📊 របាយការណ៍ & ស្ថិតិ", 
        "🗓️ កំណត់ថ្ងៃសម្រាក", 
        "⚙️ គ្រប់គ្រងសេវាកម្ម", 
        "👤 ប្រវត្តិអតិថិជន"
    ])

    # Tab 1: គ្រប់គ្រងការកក់ & ប្តូរ Status
    with tab1:
        st.subheader("📋 បញ្ជីការកក់ និងផ្លាស់ប្តូរស្ថានភាព")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        if not df_bookings.empty:
            filter_status = st.selectbox("តម្រងតាមស្ថានភាព:", ["ទាំងអស់ (All)", "Pending", "Confirmed", "Completed", "Cancelled"])
            
            df_display = df_bookings.copy()
            if filter_status != "ទាំងអស់ (All)":
                df_display = df_display[df_display["Status"] == filter_status]

            st.dataframe(
                df_display[["Customer Name", "Phone", "Services", "Staff", "Date", "Time", "Total Price", "Status", "Note"]],
                use_container_width=True, hide_index=True
            )

            st.markdown("---")
            st.subheader("⚙️ ធ្វើបច្ចុប្បន្នភាព Status ឬលុបការកក់")
            
            booking_map = {
                f"Row {r['sheet_row']} | {r['Customer Name']} ({r['Phone']}) - {r['Date']} {r['Time']} [{r['Status']}]": r
                for _, r in df_display.iterrows()
            }
            
            if booking_map:
                selected_b_label = st.selectbox("ជ្រើសរើសអតិថិជន:", list(booking_map.keys()))
                selected_b = booking_map[selected_b_label]

                col_st1, col_st2, col_st3, col_st4 = st.columns(4)
                
                if col_st1.button("🟢 បញ្ជាក់ (Confirm)", use_container_width=True):
                    requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": selected_b["sheet_row"], "status": "Confirmed"})
                    st.success("✅ បានប្តូរទៅ Confirmed")
                    st.cache_data.clear()
                    st.rerun()

                if col_st2.button("🔵 បញ្ចប់ (Complete)", use_container_width=True):
                    requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": selected_b["sheet_row"], "status": "Completed"})
                    st.success("✅ បានប្តូរទៅ Completed")
                    st.cache_data.clear()
                    st.rerun()

                if col_st3.button("🔴 បោះបង់ (Cancel)", use_container_width=True):
                    requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": selected_b["sheet_row"], "status": "Cancelled"})
                    st.warning("⚠️ បានប្តូរទៅ Cancelled")
                    st.cache_data.clear()
                    st.rerun()

                if col_st4.button("🗑️ លុបចោល (Delete)", type="primary", use_container_width=True):
                    requests.post(APPS_SCRIPT_URL, json={"action": "delete_booking", "row_index": selected_b["sheet_row"]})
                    st.error("🗑️ បានលុបទិន្នន័យជោគជ័យ")
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.info("មិនទាន់មានទិន្នន័យកក់ឡើយ។")

    # Tab 2: របាយការណ៍ & ស្ថិតិ
    with tab2:
        st.subheader("📊 របាយការណ៍ប្រាក់ចំណូល និងស្ថិតិ")
        if not df_bookings.empty:
            completed_b = df_bookings[df_bookings["Status"].isin(["Completed", "Confirmed"])]
            
            m1, m2, m3 = st.columns(3)
            m1.metric("💰 ប្រាក់ចំណូលសរុប (Completed/Confirmed)", f"${completed_b['Total Price'].sum():.2f}")
            m2.metric("📈 ចំនួនការកក់សរុប", len(df_bookings))
            m3.metric("✅ ការកក់បានសម្រេច", len(df_bookings[df_bookings["Status"] == "Completed"]))

            st.markdown("---")
            c_graph1, c_graph2 = st.columns(2)
            
            with c_graph1:
                st.subheader("🔥 ជាង/បុគ្គលិកដែលមានការកក់ច្រើនជាងគេ")
                staff_counts = df_bookings["Staff"].value_counts()
                st.bar_chart(staff_counts)

            with c_graph2:
                st.subheader("📌 ចំនួនការកក់តាមស្ថានភាព")
                status_counts = df_bookings["Status"].value_counts()
                st.bar_chart(status_counts)
        else:
            st.info("មិនទាន់មានទិន្នន័យគ្រប់គ្រាន់សម្រាប់បង្ហាញស្ថិតិ។")

    # Tab 3: កំណត់ថ្ងៃសម្រាក / បិទហាង
    with tab3:
        st.subheader("🗓️ គ្រប់គ្រងថ្ងៃបិទហាង/សម្រាក")
        with st.form("block_date_form", clear_on_submit=True):
            b_date_input = st.date_input("ជ្រើសរើសថ្ងៃត្រូវបិទហាង", datetime.now())
            b_reason_input = st.text_input("មូលហេតុ (ឧ. ថ្ងៃបុណ្យភ្ជុំបិណ្ឌ, ជួសជុលហាង)")
            if st.form_submit_button("🔒 បន្ថែមថ្ងៃបិទហាង"):
                requests.post(APPS_SCRIPT_URL, json={"action": "add_blocked_date", "date": str(b_date_input), "reason": b_reason_input.strip()})
                st.success(f"✅ បានកំណត់បិទហាងនៅថ្ងៃ {b_date_input}!")
                st.cache_data.clear()
                st.rerun()

        st.markdown("---")
        st.subheader("📋 បញ្ជីថ្ងៃដែលបានបិទ")
        if blocked_dates_list:
            for b_item in blocked_dates_list:
                cb1, cb2 = st.columns([4, 1])
                cb1.warning(f"📅 **ថ្ងៃ {b_item['date']}** | មូលហេតុ: {b_item['reason']}")
                if cb2.button("🔓 ដកចេញ", key=f"unblock_{b_item['row_index']}"):
                    requests.post(APPS_SCRIPT_URL, json={"action": "remove_blocked_date", "row_index": b_item['row_index']})
                    st.success("✅ បានបើកថ្ងៃនេះវិញជោគជ័យ!")
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.info("គ្មានថ្ងៃបិទហាងឡើយ។")

    # Tab 4: គ្រប់គ្រងសេវាកម្ម
    with tab4:
        st.subheader("➕ បន្ថែមសេវាកម្មថ្មី")
        with st.form("add_service_form", clear_on_submit=True):
            new_s_name = st.text_input("ឈ្មោះសេវាកម្ម*")
            new_s_price = st.number_input("តម្លៃ ($)*", min_value=0.0, step=0.5)
            new_s_desc = st.text_input("ការពិពណ៌នា")
            if st.form_submit_button("➕ បន្ថែមសេវាកម្ម") and new_s_name.strip():
                requests.post(APPS_SCRIPT_URL, json={"action": "add_service", "service_name": new_s_name.strip(), "price": new_s_price, "description": new_s_desc.strip()})
                st.success("✅ បានបន្ថែមសេវាកម្មថ្មីជោគជ័យ!")
                st.cache_data.clear()

        st.markdown("---")
        st.subheader("✏️ កែប្រែតម្លៃសេវាកម្ម")
        if services_dict:
            selected_s_edit = st.selectbox("ជ្រើសរើសសេវាកម្ម", list(services_dict.keys()))
            updated_price = st.number_input("តម្លៃថ្មី ($)", value=float(services_dict[selected_s_edit]), min_value=0.0, step=0.5)
            if st.button("💾 រក្សាទុកតម្លៃថ្មី"):
                requests.post(APPS_SCRIPT_URL, json={"action": "update_service", "service_name": selected_s_edit, "price": updated_price})
                st.success("✅ បានកែប្រែតម្លៃជោគជ័យ!")
                st.cache_data.clear()

    # Tab 5: ប្រវត្តិអតិថិជន
    with tab5:
        st.subheader("👤 ទិន្នន័យ & ប្រវត្តិអតិថិជន")
        if not df_bookings.empty:
            cust_group = df_bookings.groupby(["Customer Name", "Phone"]).agg(
                Total_Visits=('Services', 'count'),
                Total_Spent=('Total Price', 'sum')
            ).reset_index()

            st.dataframe(cust_group, use_container_width=True, hide_index=True)
        else:
            st.info("មិនទាន់មានទិន្នន័យអតិថិជនឡើយ។")
