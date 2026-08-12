import streamlit as st
import requests
import pandas as pd
import math
import html
import re
from datetime import datetime, time, timedelta

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="អូនឡែន សម្រស់ - កក់ម៉ោង",
    page_icon="💆‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Kantumruy Pro', sans-serif;
    }
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(236, 72, 153, 0.3);
    }
    .hero-title {
        font-size: 32px;
        font-weight: 700;
        margin: 0;
    }
    .hero-subtitle {
        font-size: 16px;
        opacity: 0.9;
        margin-top: 5px;
    }

    .points-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #f59e0b;
        border-left: 6px solid #f59e0b;
        padding: 18px;
        border-radius: 14px;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .section-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #f472b6;
        margin-bottom: 15px;
    }

    .summary-box {
        background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%);
        border: 2px solid #6366f1;
        border-radius: 20px;
        padding: 25px;
        position: sticky;
        top: 20px;
    }
    .total-price-tag {
        font-size: 36px;
        font-weight: 700;
        color: #38bdf8;
        text-align: center;
        margin: 15px 0;
    }

    /* 80mm Thermal Receipt Styling */
    .receipt-80mm {
        width: 320px;
        background-color: #ffffff;
        color: #000000;
        padding: 18px;
        border-radius: 8px;
        font-family: 'Courier New', Courier, monospace;
        margin: 0 auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .receipt-80mm .header {
        text-align: center;
        margin-bottom: 12px;
    }
    .receipt-80mm .title {
        font-size: 20px;
        font-weight: bold;
    }
    .receipt-80mm .subtitle {
        font-size: 11px;
        color: #444444;
    }
    .receipt-80mm .item-row {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin: 4px 0;
    }
    .receipt-80mm .item-label {
        color: #333333;
    }
    .receipt-80mm .item-val {
        text-align: right;
    }
    .receipt-80mm .dashed-line {
        border-bottom: 1px dashed #000000;
        margin: 8px 0;
    }
    .receipt-80mm .total-row {
        display: flex;
        justify-content: space-between;
        font-weight: bold;
        font-size: 16px;
        margin-top: 6px;
    }
    .receipt-80mm .footer {
        text-align: center;
        font-size: 11px;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECRETS & HTTP PERFORMANCE POOL
# ==========================================
APPS_SCRIPT_URL = st.secrets.get(
    "APPS_SCRIPT_URL", 
    "https://script.google.com/macros/s/AKfycbwlwyd3zHFO-9EzByegad9As7ti6KgwN-dLuZJl-219t6Ez97jpC_wjWMhpUkmWtGhw/exec"
)
API_SECRET_KEY = st.secrets.get("API_SECRET_KEY", "OUNLEN_SALON_SECURE_API_KEY_2026")
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "123456")
DEFAULT_PRODUCT_IMG = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500"

@st.cache_resource
def get_http_session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

http_client = get_http_session()

def clean_input(text):
    if not text:
        return ""
    return html.escape(str(text).strip())

def validate_phone(phone_str):
    clean_p = re.sub(r"[^\d]", "", str(phone_str))
    if len(clean_p) >= 8:
        return clean_p
    return None

def get_cambodia_now():
    return datetime.utcnow() + timedelta(hours=7)

def send_telegram_alert(msg_text):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            http_client.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg_text, "parse_mode": "Markdown"}, timeout=5)
        except Exception:
            pass

def calculate_user_points(phone, df_bookings, members_dict):
    clean_p = validate_phone(phone)
    is_member = clean_p in members_dict if clean_p else False
    
    if not is_member or df_bookings.empty or not clean_p:
        return {"earned": 0, "redeemed": 0, "balance": 0, "is_member": is_member}
    
    user_b = df_bookings[(df_bookings["Phone"].str.contains(clean_p, na=False)) & (df_bookings["Status"] != "Cancelled")]
    if user_b.empty:
        return {"earned": 0, "redeemed": 0, "balance": 0, "is_member": True}

    total_earned = user_b["Points Earned"].sum()
    total_redeemed = user_b["Points Redeemed"].sum()
    balance = max(0, total_earned - total_redeemed)

    return {"earned": int(total_earned), "redeemed": int(total_redeemed), "balance": int(balance), "is_member": True}

# ==========================================
# 3. DATA LOADING WITH AUTH & CACHING
# ==========================================
@st.cache_data(ttl=10)
def load_all_data():
    try:
        url = f"{APPS_SCRIPT_URL}?api_key={API_SECRET_KEY}"
        res = http_client.get(url, timeout=12)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"bookings": [], "services": [], "blocked_dates": [], "products": [], "promo_codes": [], "reviews": [], "settings": [], "members": []}

data = load_all_data()

# Settings
settings_dict = {}
if len(data.get("settings", [])) > 1:
    for r in data["settings"][1:]:
        if len(r) >= 2:
            settings_dict[str(r[0])] = str(r[1])

LOW_STOCK_THRESHOLD = int(settings_dict.get("low_stock_threshold", 5))
POINTS_PER_DOLLAR = float(settings_dict.get("points_per_dollar", 1.0))
POINTS_REDEEM_RATE = float(settings_dict.get("points_redeem_rate", 10.0))

# Members Dictionary
members_dict = {}
if len(data.get("members", [])) > 1:
    for idx, r in enumerate(data["members"][1:]):
        if len(r) >= 2 and r[0]:
            clean_p = validate_phone(r[0])
            if clean_p:
                members_dict[clean_p] = {
                    "row_index": idx + 2,
                    "name": clean_input(r[1]),
                    "date": str(r[2]).split("T")[0] if len(r) > 2 else ""
                }

# Services
services_list = []
if len(data.get("services", [])) > 1:
    for idx, r in enumerate(data["services"][1:]):
        if not r or not r[0]: continue
        try:
            p_val = float(str(r[1]).replace("$", "").replace(",", "").strip()) if len(r) > 1 and r[1] != "" else 0.0
            services_list.append({
                "row_index": idx + 2,
                "name": clean_input(r[0]),
                "price": p_val,
                "desc": clean_input(r[2]) if len(r) > 2 and r[2] else ""
            })
        except Exception: pass

# Products
products_list = []
low_stock_items = []
if len(data.get("products", [])) > 1:
    for idx, r in enumerate(data["products"][1:]):
        row = list(r) + [""] * (5 - len(r))
        try:
            stk = int(row[3]) if str(row[3]).isdigit() else 0
            p_item = {
                "row_index": idx + 2,
                "name": clean_input(row[0]),
                "price": float(row[1]) if row[1] != "" else 0.0,
                "image_url": str(row[2]) if row[2] else DEFAULT_PRODUCT_IMG,
                "stock": stk,
                "desc": clean_input(row[4])
            }
            products_list.append(p_item)
            if stk <= LOW_STOCK_THRESHOLD:
                low_stock_items.append(p_item)
        except Exception: pass

# Bookings
df_bookings = pd.DataFrame()
if len(data.get("bookings", [])) > 1:
    b_rows = []
    for idx, r in enumerate(data["bookings"][1:]):
        row = list(r) + [""] * (15 - len(r))
        try:
            b_rows.append({
                "sheet_row": idx + 2,
                "Created At": clean_input(row[0]),
                "Customer Name": clean_input(row[1]),
                "Phone": clean_input(str(row[2]).replace("'", "")),
                "Services": clean_input(row[3]),
                "Staff": clean_input(row[4]),
                "Date": str(row[5]).split("T")[0],
                "Time": clean_input(row[6]),
                "Note": clean_input(row[7]),
                "Status": clean_input(row[8]) if row[8] else "Pending",
                "Total Price": float(row[9]) if row[9] != "" else 0.0,
                "Deposit": clean_input(row[10]),
                "Products": clean_input(row[11]),
                "Points Earned": int(row[12]) if str(row[12]).isdigit() else 0,
                "Points Redeemed": int(row[13]) if str(row[13]).isdigit() else 0,
                "Promo Code": clean_input(row[14])
            })
        except Exception: pass
    df_bookings = pd.DataFrame(b_rows)

# Promo Codes
promo_dict = {}
if len(data.get("promo_codes", [])) > 1:
    for r in data["promo_codes"][1:]:
        if len(r) >= 2 and (len(r) < 3 or str(r[2]).lower() == "active"):
            try: promo_dict[clean_input(r[0]).upper()] = float(r[1])
            except: pass

# Blocked Dates
blocked_dates_dict = {}
if len(data.get("blocked_dates", [])) > 1:
    for r in data["blocked_dates"][1:]:
        if len(r) >= 1:
            blocked_dates_dict[str(r[0]).split("T")[0]] = clean_input(r[1]) if len(r) > 1 else "ថ្ងៃសម្រាក"

# Reviews
reviews_list = []
if len(data.get("reviews", [])) > 1:
    for idx, r in enumerate(data["reviews"][1:]):
        row = list(r) + [""] * (5 - len(r))
        try:
            reviews_list.append({
                "row_index": idx + 2,
                "date": str(row[0]).split("T")[0],
                "name": clean_input(row[1]),
                "phone": clean_input(str(row[2]).replace("'", "")),
                "rating": int(row[3]) if str(row[3]).isdigit() else 5,
                "comment": clean_input(row[4])
            })
        except Exception: pass

if "selected_slot" not in st.session_state:
    st.session_state.selected_slot = None

# ==========================================
# 4. CLIENT INTERFACE
# ==========================================
mode = st.query_params.get("mode", "client")

if mode == "client":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">✨ អូនឡែន សម្រស់ - កក់ម៉ោង</div>
        <div class="hero-subtitle">កក់ម៉ោងដើម្បីទទួលសេវាកម្ម ថែរក្សាសម្រស់ និងសន្សំពិន្ទុដើម្បីទទួលបានកាបញ្ចុះតម្លៃ</div>
    </div>
    """, unsafe_allow_html=True)

    tab_c1, tab_c2, tab_c3 = st.tabs([
        "💆‍♀️ កក់សេវាកម្ម & ទិញផលិតផល",
        "🧾 ពិនិត្យមើលវិក្កយបត្រ",
        "⭐️ ការវាយតម្លៃពីអតិថិជន"
    ])

    with tab_c1:
        col_main, col_summary = st.columns([1.8, 1], gap="large")

        with col_main:
            # 1. ព័ត៌មានអតិថិជន
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">👤 1. ព័ត៌មានអតិថិជន (Customer Information)</div>', unsafe_allow_html=True)
            ic1, ic2 = st.columns(2)
            cust_name = ic1.text_input("ឈ្មោះ / Name*", placeholder="ឧ. លី ស្រីឡែន")
            cust_phone = ic2.text_input("លេខទូរស័ព្ទ / Phone Number*", placeholder="ឧ. 067​​​969877")

            valid_p = validate_phone(cust_phone)
            points_info = calculate_user_points(cust_phone, df_bookings, members_dict)
            
            if cust_phone.strip():
                if not valid_p:
                    st.warning("⚠️ សូមបញ្ចូលលេខទូរស័ព្ទឱ្យបានត្រឹមត្រូវ (យ៉ាងហោចណាស់ ៨ ខ្ទង់)")
                elif points_info["is_member"]:
                    m_name = members_dict[valid_p]["name"]
                    st.markdown(f"""
                    <div class="points-card">
                        <b>🪙 សមតុល្យពិន្ទុរបស់អ្នក៖ <span style="color:#f59e0b; font-size:20px;">{points_info['balance']} Points</span></b><br>
                        • សមាជិក៖ <b>{m_name}</b><br>
                        • សរុបពិន្ទុសន្សំបាន៖ <b>{points_info['earned']} Points</b> | ប្រើប្រាស់រួច៖ <b>{points_info['redeemed']} Points</b><br>
                        <small>💡 លក្ខខណ្ឌ៖ <b>{POINTS_REDEEM_RATE:.0f} Points = $1.00</b> បញ្ចុះតម្លៃ | ចំណាយ <b>$1.00 = {POINTS_PER_DOLLAR:.1f} Points</b></small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("ℹ️ **លោកអ្នកជាអតិថិជនទូទៅ** (មិនទាន់បានចុះឈ្មោះសមាជិកសន្សំពិន្ទុ)។ ការសន្សំពិន្ទុ និងប្រើប្រាស់ពិន្ទុបញ្ចុះតម្លៃ គឺសម្រាប់តែអតិថិជនដែលបានចុះឈ្មោះសមាជិកប៉ុណ្ណោះ។ សូមទាក់ទងហាងដើម្បីចុះឈ្មោះសមាជិក!")
            st.markdown('</div>', unsafe_allow_html=True)

            # 2. ជ្រើសរើសសេវាកម្ម
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">💆‍♀️ 2. ជ្រើសរើសសេវាកម្ម</div>', unsafe_allow_html=True)
            sel_services = []
            services_total = 0.0

            if services_list:
                sc_cols = st.columns(2)
                for idx, srv in enumerate(services_list):
                    with sc_cols[idx % 2]:
                        if st.checkbox(f"**{srv['name']}**", key=f"srv_check_{idx}"):
                            sel_services.append(srv['name'])
                            services_total += srv['price']
                        st.caption(f"តម្លៃសេវាកម្ម: **${srv['price']:.2f}**" + (f" | {srv['desc']}" if srv['desc'] else ""))
            else:
                st.info("ℹ️ មិនទាន់មានសេវាកម្មក្នុងប្រព័ន្ធនៅឡើយទេ")
            st.markdown('</div>', unsafe_allow_html=True)

            # 3. ទំនិញថែរក្សាសម្រស់
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">🛍️ 3. ទិញផលិតផលបន្ថែម</div>', unsafe_allow_html=True)
            selected_products = {}
            ordered_items_list = []
            products_total = 0.0

            if products_list:
                p_cols = st.columns(3)
                for i, prod in enumerate(products_list):
                    with p_cols[i % 3]:
                        st.image(prod["image_url"], use_container_width=True)
                        st.markdown(f"**{prod['name']}**")
                        st.markdown(f"<span style='color:#38bdf8; font-weight:bold;'>${prod['price']:.2f}</span>", unsafe_allow_html=True)
                        st.caption(f"ស្តុកសល់: {prod['stock']}")
                        
                        qty = st.number_input("ចំនួន", min_value=0, max_value=prod['stock'], key=f"prod_qty_{i}")
                        if qty > 0:
                            selected_products[prod['name']] = {"price": prod['price'], "qty": qty}
                            ordered_items_list.append({"name": prod['name'], "qty": qty})
                            products_total += prod['price'] * qty
            st.markdown('</div>', unsafe_allow_html=True)

            # 4. កាលបរិច្ឆេទ & ម៉ោង
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">⏰ 4. កាលបរិច្ឆេទ & ជាងទទួលបន្ទុក</div>', unsafe_allow_html=True)
            dt1, dt2 = st.columns(2)
            staff = dt1.selectbox("អ្នកផ្តល់សេវាកម្ម", ["ស្រីឡែន (ម្ចាស់ហាង)", "បុគ្គលិកជំនាញ"])
            
            book_date = dt2.date_input("ថ្ងៃណាត់ជួប / Date:", get_cambodia_now().date())
            book_date_str = str(book_date)
            is_blocked = book_date_str in blocked_dates_dict

            all_slots = [time(h, m).strftime("%I:%M %p") for h in range(8, 20) for m in (0, 30)]
            booked_slots = df_bookings[(df_bookings["Date"] == book_date_str) & (df_bookings["Status"] != "Cancelled")]["Time"].tolist() if not df_bookings.empty else []
            
            st.write("ជ្រើសរើសម៉ោងទំនេរ (Time Slot):")
            if is_blocked:
                st.error(f"❌ ហាងបិទសម្រាក៖ {blocked_dates_dict[book_date_str]}")
                st.session_state.selected_slot = None
            else:
                slot_cols = st.columns(4)
                for idx, slot in enumerate(all_slots):
                    s_col = slot_cols[idx % 4]
                    is_booked = slot in booked_slots
                    btn_type = "primary" if st.session_state.selected_slot == slot else "secondary"
                    
                    if is_booked:
                        s_col.button(f"🔒 {slot}", key=f"slot_btn_{idx}", disabled=True, use_container_width=True)
                    else:
                        if s_col.button(f"🕒 {slot}", key=f"slot_btn_{idx}", type=btn_type, use_container_width=True):
                            st.session_state.selected_slot = slot
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # SUMMARY SIDEBAR
        with col_summary:
            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
            st.markdown('<h3 style="color:white; margin-top:0;">ប្រាក់សរុបត្រូវការទូទាត់</h3>', unsafe_allow_html=True)
            
            subtotal = services_total + products_total
            
            promo_input = clean_input(st.text_input("🎟️ Promo Code (បើមាន):")).upper()
            promo_discount = 0.0
            if promo_input in promo_dict:
                promo_discount = promo_dict[promo_input]
                st.success(f"🎉 ទទួលបានការបញ្ចុះតម្លៃ Promo: -${promo_discount:.2f}")

            subtotal_after_promo = max(0.0, subtotal - promo_discount)
            redeem_points = 0
            points_discount = 0.0

            if points_info["is_member"] and points_info['balance'] >= POINTS_REDEEM_RATE and subtotal_after_promo > 0:
                max_redeem_by_subtotal = int(subtotal_after_promo * POINTS_REDEEM_RATE)
                max_usable_points = min(points_info['balance'], max_redeem_by_subtotal)
                
                if st.checkbox("🎁 ប្រើប្រាស់ពិន្ទុប្តូរការបញ្ចុះតម្លៃ"):
                    step_val = int(POINTS_REDEEM_RATE) if POINTS_REDEEM_RATE >= 1 else 1
                    redeem_points = st.number_input(
                        f"ចំនួនពិន្ទុ (អតិបរមា {max_usable_points} Pts):",
                        min_value=int(POINTS_REDEEM_RATE),
                        max_value=max_usable_points,
                        step=step_val,
                        value=min(int(POINTS_REDEEM_RATE), max_usable_points)
                    )
                    points_discount = redeem_points / POINTS_REDEEM_RATE

            final_total = max(0.0, subtotal_after_promo - points_discount)
            
            if points_info["is_member"]:
                earned_points_new = math.floor(final_total * POINTS_PER_DOLLAR)
            else:
                earned_points_new = 0

            st.markdown("<hr style='border-color:#334155;'>", unsafe_allow_html=True)
            st.markdown(f"សរុបសេវា + ទំនិញ៖ **${subtotal:.2f}**")
            if promo_discount > 0: st.markdown(f"បញ្ចុះតម្លៃ Promo Code៖ <span style='color:#f43f5e;'>-${promo_discount:.2f}</span>", unsafe_allow_html=True)
            if points_discount > 0: st.markdown(f"ដកពិន្ទុប្រើប្រាស់ (-{redeem_points} Pts)៖ <span style='color:#f43f5e;'>-${points_discount:.2f}</span>", unsafe_allow_html=True)
            
            st.markdown(f'<div class="total-price-tag">${final_total:.2f}</div>', unsafe_allow_html=True)
            
            if points_info["is_member"]:
                st.info(f"🪙 ការកក់នេះនឹងទទួលបាន៖ **+{earned_points_new} Points**")
            else:
                st.caption("ℹ️ អតិថិជនទូទៅមិនទទួលបានពិន្ទុទេ")

            if st.session_state.selected_slot:
                st.success(f"ម៉ោងជ្រើសរើស៖ **{st.session_state.selected_slot}**")
            else:
                st.warning("សូមជ្រើសរើសម៉ោងណាត់ជួប")

            if st.button("✅ បញ្ជាក់ការកក់ & បញ្ជាទិញ", type="primary", use_container_width=True):
                clean_name = clean_input(cust_name)
                clean_p = validate_phone(cust_phone)

                if not clean_name or not clean_p:
                    st.error("❌ សូមបញ្ចូលឈ្មោះ និងលេខទូរស័ព្ទឱ្យបានត្រឹមត្រូវ!")
                elif not sel_services and not selected_products:
                    st.error("❌ សូមជ្រើសរើសសេវាកម្ម ឬទំនិញយ៉ាងហោចណាស់មួយ!")
                elif is_blocked or not st.session_state.selected_slot:
                    st.error("❌ សូមជ្រើសរើសម៉ោងដែលទំនេរ!")
                else:
                    prod_str = ", ".join([f"{k} (x{v['qty']})" for k, v in selected_products.items()]) if selected_products else "None"
                    payload = {
                        "api_key": API_SECRET_KEY,
                        "action": "add_booking",
                        "customer_name": clean_name,
                        "phone": clean_p,
                        "service": ", ".join(sel_services),
                        "staff": staff,
                        "date": book_date_str,
                        "time": st.session_state.selected_slot,
                        "note": "",
                        "status": "Pending",
                        "total_price": final_total,
                        "deposit": "None",
                        "products_ordered": prod_str,
                        "points_earned": earned_points_new,
                        "points_redeemed": redeem_points,
                        "promo_code": promo_input if promo_input in promo_dict else "None",
                        "ordered_items_list": ordered_items_list
                    }
                    
                    try:
                        with st.spinner("⏳ កំពុងរក្សាទុកការកក់..."):
                            res = http_client.post(APPS_SCRIPT_URL, json=payload, timeout=15)
                        
                        if res.status_code == 200:
                            send_telegram_alert(
                                f"🔔 *ការកក់ថ្មីបានចូល!*\n\n"
                                f"👤 *អតិថិជន:* {clean_name} ({'សមាជិក' if points_info['is_member'] else 'អតិថិជនទូទៅ'})\n"
                                f"📞 *ទូរស័ព្ទ:* `{clean_p}`\n"
                                f"💆‍♀️ *សេវា:* {', '.join(sel_services)}\n"
                                f"🛍️ *ទំនិញ:* {prod_str}\n"
                                f"📅 *ថ្ងៃណាត់:* {book_date_str} @ {st.session_state.selected_slot}\n"
                                f"💰 *សរុប:* ${final_total:.2f}\n"
                                f"🪙 *ពិន្ទុបានសន្សំ:* +{earned_points_new} Pts | *បានប្រើ:* -{redeem_points} Pts"
                            )
                            st.balloons()
                            st.success("🎉 កក់បានជោគជ័យ! សូមពិនិត្យមើលវិក្កយបត្រក្នុង Tab ទី ២។")
                            st.cache_data.clear()
                        else:
                            st.error("❌ មានបញ្ហាក្នុងការភ្ជាប់ទៅប្រព័ន្ធ!")
                    except Exception as e:
                        st.error(f"❌ កើតមានកំហុស៖ {e}")

            st.markdown('</div>', unsafe_allow_html=True)

    # TAB 2: RECEIPT (80mm Thermal Receipt Format)
    with tab_c2:
        st.subheader("🔍 ពិនិត្យមើលវិក្កយបត្រ (Digital Receipt 80mm)")
        search_phone = validate_phone(st.text_input("បញ្ចូលលេខទូរស័ព្ទដើម្បីទាញយកវិក្កយបត្រ:", key="search_receipt_input"))
        
        if search_phone and not df_bookings.empty:
            matched_df = df_bookings[df_bookings["Phone"].str.contains(search_phone, na=False)]
            if not matched_df.empty:
                for _, row in matched_df.iterrows():
                    created_date = str(row['Created At']).split("T")[0] if "T" in str(row['Created At']) else str(row['Created At'])
                    appt_date = str(row['Date']).split("T")[0] if "T" in str(row['Date']) else str(row['Date'])
                    
                    st.markdown(f"""
                    <div class="receipt-80mm">
                        <div class="header">
                            <div class="title">អូនឡែន សម្រស់</div>
                            <div class="subtitle">ភូមិ ដំណាក់កុយ ក្រុងកំពង់ឆ្នាំង | Tel: 067 969 877</div>
                        </div>
                        
                        <div class="item-row">
                            <span class="item-label">កាលបរិច្ឆេទកក់:</span>
                            <span class="item-val">{created_date}</span>
                        </div>
                        <div class="item-row">
                            <span class="item-label">អតិថិជន:</span>
                            <span class="item-val"><b>{row['Customer Name']}</b></span>
                        </div>
                        <div class="item-row">
                            <span class="item-label">លេខទូរស័ព្ទ:</span>
                            <span class="item-val">{row['Phone']}</span>
                        </div>
                        <div class="item-row">
                            <span class="item-label">ថ្ងៃណាត់ជួប:</span>
                            <span class="item-val">{appt_date} @ {row['Time']}</span>
                        </div>
                        <div class="item-row">
                            <span class="item-label">អ្នកផ្តល់សេវាកម្ម:</span>
                            <span class="item-val">{row['Staff']}</span>
                        </div>
                        
                        <div class="dashed-line"></div>
                        
                        <div class="item-row">
                            <span class="item-label">សេវាកម្ម:</span>
                            <span class="item-val">{row['Services']}</span>
                        </div>
                        <div class="item-row">
                            <span class="item-label">ទំនិញបញ្ជាទិញ:</span>
                            <span class="item-val">{row['Products']}</span>
                        </div>
                        
                        <div class="dashed-line"></div>
                        
                        <div class="item-row">
                            <span class="item-label">ពិន្ទុទទួលបាន:</span>
                            <span class="item-val">+{row['Points Earned']} Pts</span>
                        </div>
                        <div class="item-row">
                            <span class="item-label">ពិន្ទុប្រើប្រាស់:</span>
                            <span class="item-val">-{row['Points Redeemed']} Pts</span>
                        </div>
                        
                        <div class="total-row">
                            <span>សរុប:</span>
                            <span>${row['Total Price']:.2f}</span>
                        </div>
                        
                        <div class="footer">
                            <div><b>Status:</b> {row['Status']}</div>
                            <div style="margin-top:3px;">សូមអរគុណ! Thank You! 🙏</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
            else:
                st.warning("មិនរកឃើញទិន្នន័យការកក់សម្រាប់លេខទូរស័ព្ទនេះទេ")

    # TAB 3: REVIEWS
    with tab_c3:
        st.subheader("⭐️ ការវាយតម្លៃ និងមតិរិះគន់")
        if reviews_list:
            avg_rating = sum(r['rating'] for r in reviews_list) / len(reviews_list)
            st.metric("ពិន្ទុវាយតម្លៃជាមធ្យម", f"⭐️ {avg_rating:.1f} / 5.0", f"សរុប {len(reviews_list)} មតិ")
        
        st.markdown("---")
        with st.form("review_form", clear_on_submit=True):
            r_name = clean_input(st.text_input("ឈ្មោះរបស់អ្នក*"))
            r_phone = validate_phone(st.text_input("លេខទូរស័ព្ទ"))
            r_stars = st.slider("ផ្តល់ពិន្ទុ (Stars)", 1, 5, 5)
            r_comment = clean_input(st.text_area("មតិរិះគន់ ឬការសរសើរ*"))
            
            if st.form_submit_button("📤 ផ្ញើការវាយតម្លៃ"):
                if r_name and r_comment:
                    http_client.post(APPS_SCRIPT_URL, json={
                        "api_key": API_SECRET_KEY,
                        "action": "add_review",
                        "customer_name": r_name,
                        "phone": r_phone or "",
                        "rating": r_stars,
                        "comment": r_comment
                    }, timeout=10)
                    st.success("✅ អរគុណសម្រាប់ការផ្តល់មតិវាយតម្លៃ!")
                    st.cache_data.clear()
                    st.rerun()

# ==========================================
# 5. ADMIN DASHBOARD
# ==========================================
elif mode == "admin":
    st.title("👑 ទំព័រសម្រាប់ម្ចាស់ហាង - អូនឡែន សម្រស់")

    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        pwd = st.text_input("Enter Admin Password:", type="password")
        if st.button("🔑 Login"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("❌ Wrong password!")
        st.stop()

    if low_stock_items:
        st.warning(f"⚠️ **ទំនិញជិតអស់ពីស្តុក (≤ {LOW_STOCK_THRESHOLD}):** " + 
                   ", ".join([f"{i['name']} (សល់ {i['stock']})" for i in low_stock_items]))

    ad_tab1, ad_tab_members, ad_tab_srv, ad_tab2, ad_tab_promo, ad_tab3, ad_tab5 = st.tabs([
        "📋 ការកក់ (Bookings)",
        "👥 សមាជិកសន្សំពិន្ទុ",
        "💆‍♀️ សេវាកម្ម",
        "🛍️ ផលិតផល & ស្តុក",
        "🎟️ Promo Code",
        "📊 វិភាគចំណូល & ពិន្ទុ",
        "⚙️ កំណត់ប្រព័ន្ធ"
    ])

    # BOOKINGS
    with ad_tab1:
        st.subheader("📋 គ្រប់គ្រងការកក់")
        if not df_bookings.empty:
            st.dataframe(df_bookings[["sheet_row", "Customer Name", "Phone", "Services", "Products", "Date", "Time", "Total Price", "Points Earned", "Points Redeemed", "Status"]], use_container_width=True)
            sel_row = st.selectbox("ជ្រើសរើស Row ID ដើម្បីប្តូរ Status:", df_bookings["sheet_row"].tolist())
            b_c1, b_c2, b_c3 = st.columns(3)
            if b_c1.button("🟢 Confirm"):
                http_client.post(APPS_SCRIPT_URL, json={"api_key": API_SECRET_KEY, "action": "update_status", "row_index": sel_row, "status": "Confirmed"}, timeout=10)
                st.cache_data.clear()
                st.rerun()
            if b_c2.button("🔵 Complete"):
                http_client.post(APPS_SCRIPT_URL, json={"api_key": API_SECRET_KEY, "action": "update_status", "row_index": sel_row, "status": "Completed"}, timeout=10)
                st.cache_data.clear()
                st.rerun()
            if b_c3.button("🔴 Cancel"):
                http_client.post(APPS_SCRIPT_URL, json={"api_key": API_SECRET_KEY, "action": "update_status", "row_index": sel_row, "status": "Cancelled"}, timeout=10)
                st.cache_data.clear()
                st.rerun()

    # MEMBERS MANAGEMENT
    with ad_tab_members:
        st.subheader("👥 គ្រប់គ្រង និងចុះឈ្មោះសមាជិកសន្សំពិន្ទុ")
        m_col1, m_col2 = st.columns([1.2, 1])
        
        with m_col1:
            st.markdown("### 📋 បញ្ជីឈ្មោះសមាជិក")
            if members_dict:
                for phone, m_info in members_dict.items():
                    mc1, mc2 = st.columns([3, 1])
                    mc1.write(f"• **{m_info['name']}** - `{phone}` (ថ្ងៃចុះឈ្មោះ: {m_info['date']})")
                    if mc2.button("🗑️ លុប", key=f"del_mem_{m_info['row_index']}"):
                        http_client.post(APPS_SCRIPT_URL, json={"api_key": API_SECRET_KEY, "action": "delete_member", "row_index": m_info['row_index']}, timeout=10)
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.info("មិនទាន់មានសមាជិកត្រូវបានចុះឈ្មោះនៅឡើយទេ")

        with m_col2:
            st.markdown("### ➕ ចុះឈ្មោះសមាជិកថ្មី")
            with st.form("add_member_form", clear_on_submit=True):
                mem_name = clean_input(st.text_input("ឈ្មោះសមាជិក*"))
                mem_phone = validate_phone(st.text_input("លេខទូរស័ព្ទ*"))
                if st.form_submit_button("➕ បញ្ចូលសមាជិក"):
                    if mem_name and mem_phone:
                        http_client.post(APPS_SCRIPT_URL, json={
                            "api_key": API_SECRET_KEY,
                            "action": "add_member",
                            "name": mem_name,
                            "phone": mem_phone
                        }, timeout=10)
                        st.success("✅ បានចុះឈ្មោះសមាជិកថ្មីជោគជ័យ!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ សូមបញ្ចូលឈ្មោះ និងលេខទូរស័ព្ទឱ្យបានត្រឹមត្រូវ!")

    # SERVICES MANAGEMENT
    with ad_tab_srv:
        st.subheader("💆‍♀️ គ្រប់គ្រងសេវាកម្ម")
        s_col1, s_col2 = st.columns([1.2, 1])

        with s_col1:
            st.markdown("### 📋 បញ្ជីសេវាកម្ម")
            if services_list:
                for srv in services_list:
                    sc1, sc2 = st.columns([3, 1])
                    sc1.write(f"• **{srv['name']}** - ${srv['price']:.2f}" + (f" ({srv['desc']})" if srv['desc'] else ""))
                    if sc2.button("🗑️ លុប", key=f"del_srv_{srv['row_index']}"):
                        http_client.post(APPS_SCRIPT_URL, json={"api_key": API_SECRET_KEY, "action": "delete_service", "row_index": srv['row_index']}, timeout=10)
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.info("មិនទាន់មានសេវាកម្មក្នុងប្រព័ន្ធនៅឡើយទេ")

        with s_col2:
            st.markdown("### ➕ បញ្ចូលសេវាកម្មថ្មី")
            with st.form("add_service_form", clear_on_submit=True):
                srv_name = clean_input(st.text_input("ឈ្មោះសេវាកម្ម*"))
                srv_price = st.number_input("តម្លៃ ($)*", min_value=0.0, step=0.5)
                srv_desc = clean_input(st.text_area("ពិពណ៌នាបន្ថែម"))
                if st.form_submit_button("➕ បញ្ចូលសេវាកម្ម"):
                    if srv_name:
                        http_client.post(APPS_SCRIPT_URL, json={
                            "api_key": API_SECRET_KEY,
                            "action": "add_service",
                            "name": srv_name,
                            "price": srv_price,
                            "desc": srv_desc
                        }, timeout=10)
                        st.success("✅ បានបញ្ចូលសេវាកម្មថ្មីជោគជ័យ!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ សូមបញ្ចូលឈ្មោះសេវាកម្ម!")

    # PRODUCTS & STOCK MANAGEMENT
    with ad_tab2:
        st.subheader("🛍️ គ្រប់គ្រងផលិតផល & ស្តុក")
        p_col1, p_col2 = st.columns([1.2, 1])

        with p_col1:
            st.markdown("### 📋 បញ្ជីផលិតផល")
            if products_list:
                for prod in products_list:
                    pc1, pc2, pc3 = st.columns([2, 1, 1])
                    pc1.write(f"• **{prod['name']}** - ${prod['price']:.2f} (ស្តុក: {prod['stock']})")
                    new_stock = pc2.number_input("ស្តុកថ្មី", min_value=0, value=prod['stock'], key=f"stk_in_{prod['row_index']}")
                    if pc2.button("💾 រក្សាទុក", key=f"up_stk_{prod['row_index']}"):
                        http_client.post(APPS_SCRIPT_URL, json={
                            "api_key": API_SECRET_KEY,
                            "action": "update_stock",
                            "row_index": prod['row_index'],
                            "stock": new_stock
                        }, timeout=10)
                        st.success("✅ បច្ចុប្បន្នភាពស្តុកបានជោគជ័យ!")
                        st.cache_data.clear()
                        st.rerun()
                    if pc3.button("🗑️ លុប", key=f"del_prod_{prod['row_index']}"):
                        http_client.post(APPS_SCRIPT_URL, json={"api_key": API_SECRET_KEY, "action": "delete_product", "row_index": prod['row_index']}, timeout=10)
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.info("មិនទាន់មានផលិតផលក្នុងប្រព័ន្ធនៅឡើយទេ")

        with p_col2:
            st.markdown("### ➕ បញ្ចូលផលិតផលថ្មី")
            with st.form("add_product_form", clear_on_submit=True):
                prod_name = clean_input(st.text_input("ឈ្មោះផលិតផល*"))
                prod_price = st.number_input("តម្លៃ ($)*", min_value=0.0, step=0.5)
                prod_img = clean_input(st.text_input("Link រូបភាព (URL)", value=DEFAULT_PRODUCT_IMG))
                prod_stock = st.number_input("ចំនួនក្នុងស្តុក", min_value=0, value=10)
                prod_desc = clean_input(st.text_area("ពិពណ៌នាបន្ថែម"))
                if st.form_submit_button("➕ បញ្ចូលផលិតផល"):
                    if prod_name:
                        http_client.post(APPS_SCRIPT_URL, json={
                            "api_key": API_SECRET_KEY,
                            "action": "add_product",
                            "name": prod_name,
                            "price": prod_price,
                            "image_url": prod_img,
                            "stock": prod_stock,
                            "desc": prod_desc
                        }, timeout=10)
                        st.success("✅ បានបញ្ចូលផលិតផលថ្មីជោគជ័យ!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ សូមបញ្ចូលឈ្មោះផលិតផល!")

    # PROMO CODES
    with ad_tab_promo:
        st.subheader("🎟️ គ្រប់គ្រង Promo Code (ការបញ្ចុះតម្លៃ)")
        pr_col1, pr_col2 = st.columns([1.2, 1])

        with pr_col1:
            st.markdown("### 📋 បញ្ជី Promo Code")
            if promo_dict:
                for code, discount in promo_dict.items():
                    prc1, prc2 = st.columns([3, 1])
                    prc1.write(f"• **{code}** - បញ្ចុះតម្លៃ: **${discount:.2f}**")
                    if prc2.button("🗑️ លុប", key=f"del_promo_{code}"):
                        http_client.post(APPS_SCRIPT_URL, json={"api_key": API_SECRET_KEY, "action": "delete_promo", "code": code}, timeout=10)
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.info("មិនទាន់មាន Promo Code នៅឡើយទេ")

        with pr_col2:
            st.markdown("### ➕ បញ្ចូល Promo Code ថ្មី")
            with st.form("add_promo_form", clear_on_submit=True):
                promo_code_in = clean_input(st.text_input("កូដបញ្ចុះតម្លៃ (Code)*")).upper()
                promo_disc_in = st.number_input("ចំនួនទឹកប្រាក់បញ្ចុះ ($)*", min_value=0.5, step=0.5)
                if st.form_submit_button("➕ បង្កើត Promo Code"):
                    if promo_code_in:
                        http_client.post(APPS_SCRIPT_URL, json={
                            "api_key": API_SECRET_KEY,
                            "action": "add_promo",
                            "code": promo_code_in,
                            "discount": promo_disc_in
                        }, timeout=10)
                        st.success("✅ បានបង្កើត Promo Code ថ្មីជោគជ័យ!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ សូមបញ្ចូលកូដបញ្ចុះតម្លៃ!")

    # ANALYTICS & REVENUE
    with ad_tab3:
        st.subheader("📊 វិភាគចំណូល & ការប្រើប្រាស់ពិន្ទុ")
        if not df_bookings.empty:
            completed_b = df_bookings[df_bookings["Status"].isin(["Completed", "Confirmed"])]
            
            total_rev = completed_b["Total Price"].sum() if not completed_b.empty else 0.0
            total_pts_given = df_bookings["Points Earned"].sum()
            total_pts_used = df_bookings["Points Redeemed"].sum()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("ចំណូលសរុប (Confirmed/Completed)", f"${total_rev:.2f}")
            m2.metric("ចំនួនការកក់សរុប", f"{len(df_bookings)}")
            m3.metric("ពិន្ទុផ្ញើជូនអតិថិជន", f"{total_pts_given} Pts")
            m4.metric("ពិន្ទុត្រូវបានប្រើប្រាស់", f"{total_pts_used} Pts")

            st.markdown("---")
            st.markdown("### 📈 តារាងការកក់តាមស្ថានភាព (Booking Status Breakdown)")
            st.bar_chart(df_bookings["Status"].value_counts())
        else:
            st.info("មិនទាន់មានទិន្នន័យសម្រាប់ធ្វើការវិភាគនៅឡើយទេ")

    # SYSTEM SETTINGS & BLOCKED DATES
    with ad_tab5:
        st.subheader("⚙️ កំណត់ប្រព័ន្ធ & ថ្ងៃសម្រាក (System Settings & Blocked Dates)")
        st1, st2 = st.columns(2)

        with st1:
            st.markdown("### 🛑 គ្រប់គ្រងថ្ងៃសម្រាកហាង (Blocked Dates)")
            with st.form("add_blocked_date_form", clear_on_submit=True):
                block_d = st.date_input("ជ្រើសរើសថ្ងៃសម្រាក", get_cambodia_now().date())
                block_reason = clean_input(st.text_input("មូលហេតុសម្រាក", value="ថ្ងៃសម្រាកបុណ្យ / ជួសជុលហាង"))
                if st.form_submit_button("➕ បន្ថែមថ្ងៃសម្រាក"):
                    http_client.post(APPS_SCRIPT_URL, json={
                        "api_key": API_SECRET_KEY,
                        "action": "add_blocked_date",
                        "date": str(block_d),
                        "reason": block_reason
                    }, timeout=10)
                    st.success("✅ បានបន្ថែមថ្ងៃសម្រាកជោគជ័យ!")
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("#### 📋 បញ្ជីថ្ងៃសម្រាក")
            if blocked_dates_dict:
                for d_str, reason in blocked_dates_dict.items():
                    bc1, bc2 = st.columns([3, 1])
                    bc1.write(f"• **{d_str}**: {reason}")
                    if bc2.button("🗑️ លុប", key=f"del_bd_{d_str}"):
                        http_client.post(APPS_SCRIPT_URL, json={"api_key": API_SECRET_KEY, "action": "delete_blocked_date", "date": d_str}, timeout=10)
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.info("មិនទាន់មានកំណត់ថ្ងៃសម្រាកនៅឡើយទេ")

        with st2:
            st.markdown("### ⚙️ កំណត់តម្លៃពិន្ទុ និងស្តុក")
            with st.form("update_settings_form"):
                new_low_stock = st.number_input("កម្រិតប្រកាសអាសន្នស្តុក (Low Stock Threshold)", min_value=1, value=LOW_STOCK_THRESHOLD)
                new_pts_dollar = st.number_input("ពិន្ទុទទួលបានក្នុង $1 (Points per $1)", min_value=0.1, value=POINTS_PER_DOLLAR, step=0.5)
                new_pts_rate = st.number_input("ចំនួនពិន្ទុដើម្បីបាន $1 បញ្ចុះតម្លៃ (Points for $1 Discount)", min_value=1.0, value=POINTS_REDEEM_RATE, step=1.0)
                
                if st.form_submit_button("💾 រក្សាទុកការកំណត់"):
                    http_client.post(APPS_SCRIPT_URL, json={
                        "api_key": API_SECRET_KEY,
                        "action": "update_settings",
                        "low_stock_threshold": new_low_stock,
                        "points_per_dollar": new_pts_dollar,
                        "points_redeem_rate": new_pts_rate
                    }, timeout=10)
                    st.success("✅ កំណត់ប្រព័ន្ធត្រូវបានរក្សាទុក!")
                    st.cache_data.clear()
                    st.rerun()
