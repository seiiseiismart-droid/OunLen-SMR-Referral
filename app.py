import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, date, time

# ----------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Appointment & Booking System",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS Styling
st.markdown("""
<style>
    .stApp {
        background-color: #fff1f2 !important;
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif;
        color: #0f172a !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, div, span {
        color: #0f172a !important;
    }

    /* Top Navigation Radio Menu */
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] > div {
        background-color: #ffffff !important;
        padding: 8px 14px !important;
        border-radius: 12px !important;
        border: 2px solid #f472b6 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] span {
        color: #831843 !important;
        font-size: 16px !important;
        font-weight: 800 !important;
    }

    /* Buttons base */
    .stButton > button {
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 800 !important;
        transition: all 0.2s ease-in-out !important;
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(225, 29, 72, 0.3) !important;
    }

    button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #9f1239 !important;
        border: 2px solid #f472b6 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }

    /* Card Box Styles */
    .booking-card {
        background: #ffffff;
        border: 2px solid #fda4af;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.04);
    }
    
    .status-badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .status-pending { background-color: #fef08a; color: #854d0e; }
    .status-confirmed { background-color: #bfdbfe; color: #1e40af; }
    .status-completed { background-color: #bbf7d0; color: #166534; }
    .status-cancelled { background-color: #fecaca; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. Data Initialization
# ----------------------------------------------------------------
if "categories" not in st.session_state:
    st.session_state.categories = ["✨ សេវាកម្មទូទៅ", "⚡ សេវាកម្ម Laser", "🧴 សេវាកម្ម ស្ប៉ា"]

if "staff_list" not in st.session_state:
    st.session_state.staff_list = [
        {"id": "ST01", "name": "អ្នកគ្រូ ឡែន", "role": "Senior Specialist"},
        {"id": "ST02", "name": "កញ្ញា មុន្នី", "role": "Facial Expert"},
        {"id": "ST03", "name": "កញ្ញា ផល្លា", "role": "Laser Specialist"}
    ]

if "services_catalog" not in st.session_state:
    st.session_state.services_catalog = [
        {"code": "S01", "category": "✨ សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ", "price": 15.0, "duration": 45},
        {"code": "S02", "category": "✨ សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីន baby Glow", "price": 15.0, "duration": 45},
        {"code": "S03", "category": "✨ សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីន college", "price": 12.5, "duration": 30},
        {"code": "S04", "category": "✨ សេវាកម្មទូទៅ", "name": "ញេចសម្អាតគ្រាប់មុន ជម្រុះកោសិកា", "price": 7.5, "duration": 40},
        {"code": "S05", "category": "✨ សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនVIP ពីមុខ ដល់ ក", "price": 25.0, "duration": 60},
        {"code": "S06", "category": "✨ សេវាកម្មទូទៅ", "name": "កក់សក់ + បិទម៉ាស", "price": 4.0, "duration": 30},
        {"code": "L01", "category": "⚡ សេវាកម្ម Laser", "name": "បាញ់ Laser ក្លៀក", "price": 5.0, "duration": 20},
        {"code": "L02", "category": "⚡ សេវាកម្ម Laser", "name": "បាញ់ Laser រោមដៃ", "price": 9.0, "duration": 30},
    ]

if "bookings_list" not in st.session_state:
    # គំរូទិន្នន័យស្រាប់
    st.session_state.bookings_list = [
        {
            "id": "BK-1001",
            "customer_name": "អ្នកស្រី លីដា",
            "customer_phone": "012345678",
            "service_name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនVIP ពីមុខ ដល់ ក",
            "staff_name": "អ្នកគ្រូ ឡែន",
            "date": str(date.today()),
            "time": "09:00",
            "price": 25.0,
            "status": "Confirmed",
            "note": "ស្បែកមុខប្រតិកម្មងាយ"
        },
        {
            "id": "BK-1002",
            "customer_name": "កញ្ញា សុភា",
            "customer_phone": "098765432",
            "service_name": "បាញ់ Laser ក្លៀក",
            "staff_name": "កញ្ញា ផល្លា",
            "date": str(date.today()),
            "time": "14:30",
            "price": 5.0,
            "status": "Pending",
            "note": ""
        }
    ]

# ----------------------------------------------------------------
# 3. Helper Functions
# ----------------------------------------------------------------
def generate_booking_ticket_html(b):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: 80mm auto; margin: 0; }}
            body {{
                font-family: 'Kantumruy Pro', 'Khmer OS Battambang', monospace;
                width: 72mm; margin: 0 auto; padding: 10px;
                background-color: #ffffff; color: #000000; font-size: 12px;
            }}
            .text-center {{ text-align: center; }}
            .dashed-line {{ border-top: 1px dashed #000; margin: 8px 0; }}
            .flex-between {{ display: flex; justify-content: space-between; margin: 4px 0; }}
            @media print {{ .no-print {{ display: none !important; }} }}
            .print-btn {{
                background-color: #e11d48; color: white; border: none;
                padding: 10px; font-size: 14px; font-weight: bold;
                border-radius: 8px; cursor: pointer; width: 100%; margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <button class="print-btn no-print" onclick="window.print()">🖨️ ព្រីនប័ណ្ណកក់ម៉ោង (Print Booking Ticket)</button>
        <div class="text-center">
            <h2 style="margin: 0; font-size: 16px;">💇‍♀️ អូនឡែន សម្រស់</h2>
            <p style="margin: 2px 0; font-size: 10px;">ប័ណ្ណទទួលការកក់ម៉ោង (Booking Ticket)</p>
        </div>
        <div class="dashed-line"></div>
        <div style="font-size: 11px;">
            <div class="flex-between"><span>លេខកក់:</span> <b>{b['id']}</b></div>
            <div class="flex-between"><span>អតិថិជន:</span> <b>{b['customer_name']}</b></div>
            <div class="flex-between"><span>ទូរស័ព្ទ:</span> <span>{b['customer_phone']}</span></div>
            <div class="dashed-line"></div>
            <div class="flex-between"><span>ថ្ងៃណាត់ជួប:</span> <b>{b['date']}</b></div>
            <div class="flex-between"><span>ម៉ោង:</span> <b>{b['time']}</b></div>
            <div class="flex-between"><span>សេវាកម្ម:</span> <span>{b['service_name']}</span></div>
            <div class="flex-between"><span>ជាងទទួលបន្ទុក:</span> <span>{b['staff_name']}</span></div>
            <div class="flex-between"><span>តម្លៃសេវា:</span> <b>${b['price']:.2f}</b></div>
            <div class="flex-between"><span>ស្ថានភាព:</span> <b>{b['status']}</b></div>
        </div>
        <div class="dashed-line"></div>
        <div class="text-center" style="margin-top: 10px; font-size: 10px;">
            <p>🙏🏻 សូមអញ្ជើញមកឱ្យបានមុន ១០នាទី! សូមអរគុណ!</p>
        </div>
    </body>
    </html>
    """

# ----------------------------------------------------------------
# 4. Main Navigation Menu
# ----------------------------------------------------------------
main_mode = st.radio(
    "📌 Navigation Menu",
    [
        "📅 កក់ម៉ោងថ្មី (New Booking)", 
        "📋 បញ្ជីកក់ម៉ោង (Manage Bookings)", 
        "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)", 
        "👩‍ស្ទាត់ជំនាញ គ្រប់គ្រងបុគ្គលិក (Staff)", 
        "📊 របាយការណ៍កក់ (Booking Report)"
    ],
    horizontal=True
)

st.markdown("---")

# ----------------------------------------------------------------
# MODE 1: NEW BOOKING (បង្កើតការកក់ថ្មី)
# ----------------------------------------------------------------
if main_mode == "📅 កក់ម៉ោងថ្មី (New Booking)":
    st.markdown("## 📅 បង្កើតការកក់ម៉ោងថ្មី (New Appointment)")
    
    col_form, col_summary = st.columns([2, 1], gap="large")

    with col_form:
        with st.form("new_booking_form", clear_on_submit=False):
            st.markdown("##### 1. ព័ត៌មានអតិថិជន")
            c1, c2 = st.columns(2)
            c_name = c1.text_input("ឈ្មោះអតិថិជន (Customer Name)*", placeholder="ឧទាហរណ៍: អ្នកស្រី គឹម")
            c_phone = c2.text_input("លេខទូរស័ព្ទ (Phone Number)*", placeholder="ឧទាហរណ៍: 012 345 678")

            st.markdown("##### 2. ជ្រើសរើសសេវាកម្ម & បុគ្គលិក")
            cat_selected = st.selectbox("ប្រភេទសេវាកម្ម", st.session_state.categories)
            
            # Filter services by category
            avail_services = [s for s in st.session_state.services_catalog if s["category"] == cat_selected]
            service_options = [f"{s['name']} (${s['price']:.2f} - {s['duration']}នាទី)" for s in avail_services]
            
            selected_s_str = st.selectbox("ជ្រើសរើសសេវាកម្ម*", service_options if service_options else ["គ្មានសេវាកម្ម"])
            
            staff_options = [f"{stf['name']} ({stf['role']})" for stf in st.session_state.staff_list]
            selected_staff_str = st.selectbox("ជ្រើសរើសជាង/បុគ្គលិក*", staff_options)

            st.markdown("##### 3. កាលបរិច្ឆេទ & ម៉ោងណាត់")
            d_col, t_col = st.columns(2)
            b_date = d_col.date_input("ថ្ងៃណាត់ជួប (Date)", date.today())
            
            # Time slots (08:00 AM - 07:00 PM)
            time_slots = [
                "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00"
            ]
            b_time = t_col.selectbox("ម៉ោងណាត់ជួប (Time Slot)", time_slots)

            b_note = st.text_area("ចំណាំបន្ថែម (Note)", placeholder="ឧទាហរណ៍: ស្បែកប្រកបដោយមុន, ប្រតិកម្មប្រេង...")

            submit_booking = st.form_submit_button("✅ រក្សាទុកការកក់ម៉ោង (Confirm Booking)", type="primary", use_container_width=True)

            if submit_booking:
                if not c_name.strip() or not c_phone.strip():
                    st.error("សូមបញ្ចូលឈ្មោះ និង លេខទូរស័ព្ទអតិថិជន!")
                elif not avail_services:
                    st.error("មិនទាន់មានសេវាកម្មក្នុងប្រភេទនេះទេ!")
                else:
                    # Get selected service object
                    selected_service = avail_services[service_options.index(selected_s_str)]
                    selected_staff = st.session_state.staff_list[staff_options.index(selected_staff_str)]

                    new_id = f"BK-{len(st.session_state.bookings_list) + 1001}"
                    booking_data = {
                        "id": new_id,
                        "customer_name": c_name.strip(),
                        "customer_phone": c_phone.strip(),
                        "service_name": selected_service["name"],
                        "staff_name": selected_staff["name"],
                        "date": str(b_date),
                        "time": b_time,
                        "price": selected_service["price"],
                        "status": "Confirmed",
                        "note": b_note.strip()
                    }
                    st.session_state.bookings_list.append(booking_data)
                    st.success(f"🎉 ការកក់ម៉ោងជោគជ័យ! លេខកក់គឺ: {new_id}")
                    st.session_state.last_booking = booking_data
                    st.rerun()

    with col_summary:
        st.markdown("### 🧾 ប័ណ្ណកក់ម៉ោងចុងក្រោយ")
        if "last_booking" in st.session_state:
            lb = st.session_state.last_booking
            st.components.v1.html(generate_booking_ticket_html(lb), height=450, scrolling=True)
        else:
            st.info("មិនទាន់មានទិន្នន័យកក់ថ្មីនៅឡើយទេ។")

# ----------------------------------------------------------------
# MODE 2: MANAGE BOOKINGS (បញ្ជី និង គ្រប់គ្រងការកក់)
# ----------------------------------------------------------------
elif main_mode == "📋 បញ្ជីកក់ម៉ោង (Manage Bookings)":
    st.markdown("## 📋 បញ្ជីកក់ម៉ោងទាំងអស់ (Booking List)")

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    search_date = filter_col1.date_input("តម្រងតាមថ្ងៃ (Filter Date)", date.today())
    search_status = filter_col2.selectbox("ស្ថានភាព (Status)", ["ទាំងអស់ (All)", "Pending", "Confirmed", "Completed", "Cancelled"])
    search_kw = filter_col3.text_input("ស្វែងរកឈ្មោះ/លេខទូរស័ព្ទ/លេខកក់")

    filtered_list = st.session_state.bookings_list

    # Filters Logic
    if search_status != "ទាំងអស់ (All)":
        filtered_list = [b for b in filtered_list if b["status"] == search_status]
    if search_kw:
        kw = search_kw.lower()
        filtered_list = [b for b in filtered_list if kw in b["customer_name"].lower() or kw in b["customer_phone"] or kw in b["id"].lower()]

    st.markdown("---")

    if not filtered_list:
        st.info("មិនមានការកក់ម៉ោងស្របតាមការស្វែងរកឡើយ!")
    else:
        for idx, b in enumerate(filtered_list):
            status_class = f"status-{b['status'].lower()}"
            
            with st.container():
                st.markdown(f"""
                <div class="booking-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 18px; font-weight: 900; color: #be123c;">#{b['id']} - {b['customer_name']} ({b['customer_phone']})</span>
                        <span class="status-badge {status_class}">{b['status']}</span>
                    </div>
                    <hr style="margin: 8px 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 14px;">
                        <span>📅 ថ្ងៃណាត់: <b>{b['date']}</b> ម៉ោង: <b>{b['time']}</b></span>
                        <span>💇‍♀️ សេវា: <b>{b['service_name']}</b></span>
                        <span>👩‍ស្ទាត់ ជាង: <b>{b['staff_name']}</b></span>
                        <span>💵 តម្លៃ: <b>${b['price']:.2f}</b></span>
                    </div>
                    {f'<div style="font-size: 12px; color: #64748b; margin-top: 5px;">📝 ចំណាំ: {b["note"]}</div>' if b["note"] else ''}
                </div>
                """, unsafe_allow_html=True)

                c_st1, c_st2, c_st3, c_st4 = st.columns([1, 1, 1, 2])
                
                # Update status buttons
                if c_st1.button("✅ Confirmed", key=f"btn_conf_{b['id']}"):
                    b["status"] = "Confirmed"
                    st.rerun()
                if c_st2.button("🎉 Completed", key=f"btn_comp_{b['id']}"):
                    b["status"] = "Completed"
                    st.rerun()
                if c_st3.button("❌ Cancelled", key=f"btn_canc_{b['id']}"):
                    b["status"] = "Cancelled"
                    st.rerun()
                if c_st4.button("🗑️ លុបចោល", key=f"btn_del_{b['id']}"):
                    st.session_state.bookings_list = [item for item in st.session_state.bookings_list if item["id"] != b["id"]]
                    st.rerun()

# ----------------------------------------------------------------
# MODE 3: SERVICE MANAGEMENT
# ----------------------------------------------------------------
elif main_mode == "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)":
    st.markdown("## 🛠️ គ្រប់គ្រងសេវាកម្ម (Manage Services)")
    col_s_add, col_s_edit = st.columns(2, gap="large")

    with col_s_add:
        st.markdown("### ➕ បន្ថែមសេវាកម្មថ្មី")
        with st.form("add_service_form", clear_on_submit=True):
            s_code = st.text_input("កូដសេវាកម្ម", placeholder="ឧទាហរណ៍: S10, L07...")
            s_name = st.text_input("ឈ្មោះសេវាកម្ម", placeholder="ឧទាហរណ៍: ម៉ាសស្កាតមុខកូនក្រមុំ")
            s_cat = st.selectbox("ប្រភេទសេវាកម្ម", st.session_state.categories)
            s_price = st.number_input("តម្លៃ ($)", min_value=0.0, value=10.0, step=0.5)
            s_dur = st.number_input("រយៈពេលធ្វើ (នាទី)", min_value=10, value=45, step=5)

            submit_add_service = st.form_submit_button("➕ បញ្ចូលសេវាកម្មថ្មី", type="primary")
            if submit_add_service:
                if not s_code.strip() or not s_name.strip():
                    st.error("សូមបញ្ចូលកូដ និង ឈ្មោះសេវាកម្ម!")
                else:
                    new_item = {
                        "code": s_code.strip().upper(),
                        "category": s_cat,
                        "name": s_name.strip(),
                        "price": float(s_price),
                        "duration": int(s_dur)
                    }
                    st.session_state.services_catalog.append(new_item)
                    st.success(f"បានបន្ថែមសេវាកម្ម '{s_name}' រួចរាល់!")
                    st.rerun()

    with col_s_edit:
        st.markdown("### 📋 បញ្ជីសេវាកម្មបច្ចុប្បន្ន")
        df_serv = pd.DataFrame(st.session_state.services_catalog)
        st.dataframe(df_serv, use_container_width=True)

# ----------------------------------------------------------------
# MODE 4: STAFF MANAGEMENT
# ----------------------------------------------------------------
elif main_mode == "👩‍ស្ទាត់ជំនាញ គ្រប់គ្រងបុគ្គលិក (Staff)":
    st.markdown("## 👩‍ស្ទាត់ជំនាញ គ្រប់គ្រងបុគ្គលិក / ជាង (Staff Management)")
    
    col_stf1, col_stf2 = st.columns(2, gap="large")
    with col_stf1:
        st.markdown("### ➕ បន្ថែមបុគ្គលិកថ្មី")
        with st.form("add_staff_form", clear_on_submit=True):
            stf_id = st.text_input("លេខសម្គាល់បុគ្គលិក (Staff ID)", value=f"ST0{len(st.session_state.staff_list)+1}")
            stf_name = st.text_input("ឈ្មោះបុគ្គលិក (Staff Name)")
            stf_role = st.text_input("ជំនាញ/តួនាទី (Role)", placeholder="ឧទាហរណ៍: Facial Expert, Hair Stylist...")
            
            if st.form_submit_button("💾 រក្សាទុកបុគ្គលិក", type="primary"):
                if stf_name.strip():
                    st.session_state.staff_list.append({"id": stf_id, "name": stf_name.strip(), "role": stf_role.strip()})
                    st.success("បន្ថែមបុគ្គលិកជោគជ័យ!")
                    st.rerun()
                else:
                    st.error("សូមបញ្ចូលឈ្មោះបុគ្គលិក!")

    with col_stf2:
        st.markdown("### 👥 បញ្ជីបុគ្គលិកបច្ចុប្បន្ន")
        df_staff = pd.DataFrame(st.session_state.staff_list)
        st.dataframe(df_staff, use_container_width=True)

# ----------------------------------------------------------------
# MODE 5: BOOKING REPORT
# ----------------------------------------------------------------
elif main_mode == "📊 របាយការណ៍កក់ (Booking Report)":
    st.markdown("## 📊 របាយការណ៍កក់ម៉ោង (Booking Statistics)")

    if not st.session_state.bookings_list:
        st.info("មិនទាន់មានទិន្នន័យកក់ម៉ោងនៅឡើយទេ!")
    else:
        df_booking = pd.DataFrame(st.session_state.bookings_list)
        
        total_bk = len(df_booking)
        completed_bk = len(df_booking[df_booking["status"] == "Completed"])
        pending_bk = len(df_booking[df_booking["status"] == "Pending"])
        confirmed_bk = len(df_booking[df_booking["status"] == "Confirmed"])
        est_revenue = df_booking[df_booking["status"] != "Cancelled"]["price"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ការកក់សរុប (Total Bookings)", f"{total_bk}")
        m2.metric("បានបញ្ចប់ (Completed)", f"{completed_bk}")
        m3.metric("រង់ចាំ/បានបញ្ជាក់ (Pending/Confirmed)", f"{pending_bk + confirmed_bk}")
        m4.metric("ចំណូលប៉ាន់ស្មាន ($)", f"${est_revenue:.2f}")

        st.markdown("---")
        st.markdown("### 📋 តារាងទិន្នន័យការកក់ម៉ោងទាំងអស់")
        st.dataframe(df_booking, use_container_width=True)
