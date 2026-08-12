import streamlit as st
import requests
import pandas as pd
import math
from datetime import datetime, time, timedelta

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="អូនឡែន សម្រស់ ",
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

    .receipt-box {
        background-color: #ffffff;
        color: #0f172a;
        padding: 25px;
        border-radius: 12px;
        border: 2px dashed #94a3b8;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONFIG & SECRETS MANAGEMENT
# ==========================================
APPS_SCRIPT_URL = st.secrets.get(
    "APPS_SCRIPT_URL", 
    "https://script.google.com/macros/s/AKfycbwlwyd3zHFO-9EzByegad9As7ti6KgwN-dLuZJl-219t6Ez97jpC_wjWMhpUkmWtGhw/exec"
)
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "123456")
DEFAULT_PRODUCT_IMG = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500"

def get_cambodia_now():
    return datetime.utcnow() + timedelta(hours=7)

def send_telegram_alert(msg_text):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg_text, "parse_mode": "Markdown"}, timeout=10)
        except Exception:
            pass

def calculate_user_points(phone, df_bookings, members_dict):
    clean_phone = phone.strip().replace("'", "")
    is_member = clean_phone in members_dict if clean_phone else False
    
    if not is_member or df_bookings.empty or not clean_phone:
        return {"earned": 0, "redeemed": 0, "balance": 0, "is_member": is_member}
    
    user_b = df_bookings[(df_bookings["Phone"].str.contains(clean_phone, na=False)) & (df_bookings["Status"] != "Cancelled")]
    if user_b.empty:
        return {"earned": 0, "redeemed": 0, "balance": 0, "is_member": True}

    total_earned = user_b["Points Earned"].sum()
    total_redeemed = user_b["Points Redeemed"].sum()
    balance = max(0, total_earned - total_redeemed)

    return {"earned": int(total_earned), "redeemed": int(total_redeemed), "balance": int(balance), "is_member": True}

# ==========================================
# 3. DATA LOADING FROM GOOGLE SHEETS
# ==========================================
@st.cache_data(ttl=5)
def load_all_data():
    try:
        res = requests.get(APPS_SCRIPT_URL, timeout=15)
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
            clean_p = str(r[0]).replace("'", "").strip()
            members_dict[clean_p] = {
                "row_index": idx + 2,
                "name": str(r[1]).strip(),
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
                "name": str(r[0]).strip(),
                "price": p_val,
                "desc": str(r[2]).strip() if len(r) > 2 and r[2] else ""
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
                "name": str(row[0]),
                "price": float(row[1]) if row[1] != "" else 0.0,
                "image_url": str(row[2]) if row[2] else DEFAULT_PRODUCT_IMG,
                "stock": stk,
                "desc": str(row[4])
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
                "Created At": str(row[0]),
                "Customer Name": str(row[1]),
                "Phone": str(row[2]).replace("'", ""),
                "Services": str(row[3]),
                "Staff": str(row[4]),
                "Date": str(row[5]).split("T")[0],
                "Time": str(row[6]),
                "Note": str(row[7]),
                "Status": str(row[8]) if row[8] else "Pending",
                "Total Price": float(row[9]) if row[9] != "" else 0.0,
                "Deposit": str(row[10]),
                "Products": str(row[11]),
                "Points Earned": int(row[12]) if str(row[12]).isdigit() else 0,
                "Points Redeemed": int(row[13]) if str(row[13]).isdigit() else 0,
                "Promo Code": str(row[14])
            })
        except Exception: pass
    df_bookings = pd.DataFrame(b_rows)

# Promo Codes
promo_dict = {}
if len(data.get("promo_codes", [])) > 1:
    for r in data["promo_codes"][1:]:
        if len(r) >= 2 and (len(r) < 3 or str(r[2]).lower() == "active"):
            try: promo_dict[str(r[0]).upper().strip()] = float(r[1])
            except: pass

# Blocked Dates
blocked_dates_dict = {}
if len(data.get("blocked_dates", [])) > 1:
    for r in data["blocked_dates"][1:]:
        if len(r) >= 1:
            blocked_dates_dict[str(r[0]).split("T")[0]] = r[1] if len(r) > 1 else "ថ្ងៃសម្រាក"

# Reviews
reviews_list = []
if len(data.get("reviews", [])) > 1:
    for idx, r in enumerate(data["reviews"][1:]):
        row = list(r) + [""] * (5 - len(r))
        try:
            reviews_list.append({
                "row_index": idx + 2,
                "date": str(row[0]).split("T")[0],
                "name": str(row[1]),
                "phone": str(row[2]).replace("'", ""),
                "rating": int(row[3]) if str(row[3]).isdigit() else 5,
                "comment": str(row[4])
            })
        except Exception: pass

if "selected_slot" not in st.session_state:
    st.session_state.selected_slot = None

# ==========================================
# 4. APPLICATION ROUTING
# ==========================================
mode = st.query_params.get("mode", "client")

if mode == "client":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">✨ អូនឡែន សម្រស់ </div>
        <div class="hero-subtitle">សូមកក់ម៉ោងដើម្បីទទួលសេវាកម្ម ថែរក្សាសម្រស់ និងសន្សំពិន្ទុដើម្បីទទួលបានកាបញ្ចុះតម្លៃ</div>
    </div>
    """, unsafe_allow_html=True)

    tab_c1, tab_c2, tab_c3 = st.tabs([
        "💆‍♀️ កក់សេវាកម្ម & ទិញទំនិញ",
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
            cust_name = ic1.text_input("ឈ្មោះអតិថិជន / Name*", placeholder="ឧ. កែវ ធីតា")
            cust_phone = ic2.text_input("លេខទូរស័ព្ទ / Phone Number*", placeholder="ឧ. 012345678")

            points_info = calculate_user_points(cust_phone, df_bookings, members_dict)
            if cust_phone.strip():
                if points_info["is_member"]:
                    m_name = members_dict[cust_phone.strip().replace("'", "")]["name"]
                    st.markdown(f"""
                    <div class="points-card">
                        <b>🪙 សមតុល្យពិន្ទុរបស់អ្នក៖ <span style="color:#f59e0b; font-size:20px;">{points_info['balance']} Points</span></b><br>
                        • សមាជិក៖ <b>{m_name}</b><br>
                        • សរុបពិន្ទុសន្សំបាន៖ <b>{points_info['earned']} Points</b> | ប្រើប្រាស់រួច៖ <b>{points_info['redeemed']} Points</b><br>
                        <small>💡 លក្ខខណ្ឌ៖ <b>{POINTS_REDEEM_RATE:.0f} Points = $1.00</b> បញ្ចុះតម្លៃ | ចំណាយ <b>$1.00 = {POINTS_PER_DOLLAR:.1f} Points</b></small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("ℹ️ **លោកអ្នកជាអតិថិជនទូទៅ** (មិនទាន់បានចុះឈ្មោះជាសមាជិកសន្សំពិន្ទុឡើយ)។ ពិន្ទុបញ្ចុះតម្លៃ គឺសម្រាប់តែអតិថិជនដែលបានចុះឈ្មោះសមាជិកប៉ុណ្ណោះ។ សូមទាក់ទងម្ចាស់ហាងដើម្បីចុះឈ្មោះសមាជិក!")
            st.markdown('</div>', unsafe_allow_html=True)

            # 2. ជ្រើសរើសសេវាកម្ម
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">💆‍♀️ 2. ជ្រើសរើសសេវាកម្ម (Beauty Services)</div>', unsafe_allow_html=True)
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
            st.markdown('<div class="section-header">🛍️ 3. ទិញទំនិញបន្ថែម (Beauty Products)</div>', unsafe_allow_html=True)
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
            staff = dt1.selectbox("ជ្រើសរើសជាង / Stylist:", ["អ្នកគ្រូ ឡែន (Master)", "ជាងជំនាញទី ១"])
            
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
            st.markdown('<h3 style="color:white; margin-top:0;">💳 សង្ខេបការទូទាត់</h3>', unsafe_allow_html=True)
            
            subtotal = services_total + products_total
            
            # Promo Code Discount
            promo_input = st.text_input("🎟️ Promo Code (បើមាន):").strip().upper()
            promo_discount = 0.0
            if promo_input in promo_dict:
                promo_discount = promo_dict[promo_input]
                st.success(f"🎉 ទទួលបានការបញ្ចុះតម្លៃ Promo: -${promo_discount:.2f}")

            # Points Discount Calculation (Only for Members)
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
            
            # Points Earning (Only for Members)
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
                if not cust_name.strip() or not cust_phone.strip():
                    st.error("❌ សូមបញ្ចូលឈ្មោះ និងលេខទូរស័ព្ទ!")
                elif not sel_services and not selected_products:
                    st.error("❌ សូមជ្រើសរើសសេវាកម្ម ឬទំនិញយ៉ាងហោចណាស់មួយ!")
                elif is_blocked or not st.session_state.selected_slot:
                    st.error("❌ សូមជ្រើសរើសម៉ោងដែលទំនេរ!")
                else:
                    prod_str = ", ".join([f"{k} (x{v['qty']})" for k, v in selected_products.items()]) if selected_products else "None"
                    payload = {
                        "action": "add_booking",
                        "customer_name": cust_name.strip(),
                        "phone": cust_phone.strip(),
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
                            res = requests.post(APPS_SCRIPT_URL, json=payload, timeout=25)
                        
                        if res.status_code == 200:
                            send_telegram_alert(
                                f"🔔 *ការកក់ថ្មីបានចូល!*\n\n"
                                f"👤 *អតិថិជន:* {cust_name.strip()} ({'សមាជិក' if points_info['is_member'] else 'អតិថិជនទូទៅ'})\n"
                                f"📞 *ទូរស័ព្ទ:* `{cust_phone.strip()}`\n"
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

    # TAB 2: RECEIPT
    with tab_c2:
        st.subheader("🔍 ពិនិត្យមើលវិក្កយបត្រ (Digital Receipt)")
        search_phone = st.text_input("បញ្ចូលលេខទូរស័ព្ទដើម្បីទាញយកវិក្កយបត្រ:").strip()
        if search_phone and not df_bookings.empty:
            matched_df = df_bookings[df_bookings["Phone"].str.contains(search_phone, na=False)]
            if not matched_df.empty:
                for _, row in matched_df.iterrows():
                    st.markdown(f"""
                    <div class="receipt-box">
                        <h3 style="text-align:center; margin:0;">🧾 អូនឡែន សម្រស់ </h3>
                        <p style="text-align:center; font-size:12px;">ភូមិដំណាក់ពពូល ក្រុងកំពង់ឆ្នាំង | Tel: 067 969 877</p>
                        <hr>
                        <p><b>កាលបរិច្ឆេទកក់:</b> {row['Created At']}</p>
                        <p><b>អតិថិជន:</b> {row['Customer Name']}</p>
                        <p><b>លេខទូរស័ព្ទ:</b> {row['Phone']}</p>
                        <p><b>ថ្ងៃណាត់ជួប:</b> {row['Date']} @ {row['Time']}</p>
                        <p><b>ធ្វើសេវាកម្មដោយ:</b> {row['Staff']}</p>
                        <hr>
                        <p><b>សេវាកម្ម:</b> {row['Services']}</p>
                        <p><b>ទំនិញបញ្ជាទិញ:</b> {row['Products']}</p>
                        <p><b>ពិន្ទុទទួលបាន:</b> +{row['Points Earned']} Points</p>
                        <p><b>ពិន្ទុប្រើប្រាស់:</b> -{row['Points Redeemed']} Points</p>
                        <h3 style="text-align:right; color:#2563eb;">សរុប៖ ${row['Total Price']:.2f}</h3>
                        <p style="text-align:center; font-size:12px;"><b>Status:</b> {row['Status']}</p>
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
            r_name = st.text_input("ឈ្មោះរបស់អ្នក*")
            r_phone = st.text_input("លេខទូរស័ព្ទ")
            r_stars = st.slider("ផ្តល់ពិន្ទុ (Stars)", 1, 5, 5)
            r_comment = st.text_area("មតិរិះគន់ ឬការសរសើរ*")
            
            if st.form_submit_button("📤 ផ្ញើការវាយតម្លៃ"):
                if r_name.strip() and r_comment.strip():
                    requests.post(APPS_SCRIPT_URL, json={
                        "action": "add_review",
                        "customer_name": r_name.strip(),
                        "phone": r_phone.strip(),
                        "rating": r_stars,
                        "comment": r_comment.strip()
                    }, timeout=20)
                    st.success("✅ អរគុណសម្រាប់ការផ្តល់មតិវាយតម្លៃ!")
                    st.cache_data.clear()
                    st.rerun()

# ==========================================
# 5. ADMIN DASHBOARD (?mode=admin)
# ==========================================
elif mode == "admin":
    st.title("👑 ម្ចាស់ហាង - អូនឡែន សម្រស់")

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
                requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": sel_row, "status": "Confirmed"}, timeout=20)
                st.cache_data.clear()
                st.rerun()
            if b_c2.button("🔵 Complete"):
                requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": sel_row, "status": "Completed"}, timeout=20)
                st.cache_data.clear()
                st.rerun()
            if b_c3.button("🔴 Cancel"):
                requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": sel_row, "status": "Cancelled"}, timeout=20)
                st.cache_data.clear()
                st.rerun()

    # MEMBERS MANAGEMENT (បន្ថែមថ្មី)
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
                        requests.post(APPS_SCRIPT_URL, json={"action": "delete_member", "row_index": m_info['row_index']}, timeout=20)
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.info("មិនទាន់មានសមាជិកត្រូវបានចុះឈ្មោះនៅឡើយទេ")

        with m_col2:
            st.markdown("### ➕ ចុះឈ្មោះសមាជិកថ្មី")
            with st.form("add_member_form", clear_on_submit=True):
                mem_name = st.text_input("ឈ្មោះសមាជិក*")
                mem_phone = st.text_input("លេខទូរស័ព្ទ*")
                if st.form_submit_button("✅ ចុះឈ្មោះសមាជិក"):
                    clean_m_phone = mem_phone.strip().replace("'", "")
                    if mem_name.strip() and clean_m_phone:
                        if clean_m_phone in members_dict:
                            st.error("❌ លេខទូរស័ព្ទនេះបានចុះឈ្មោះរួចហើយ!")
                        else:
                            requests.post(APPS_SCRIPT_URL, json={
                                "action": "add_member",
                                "customer_name": mem_name.strip(),
                                "phone": clean_m_phone
                            }, timeout=20)
                            st.success("🎉 ចុះឈ្មោះសមាជិកបានជោគជ័យ!")
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.error("❌ សូមបញ្ចូលឈ្មោះ និងលេខទូរស័ព្ទ!")

    # SERVICES
    with ad_tab_srv:
        st.subheader("💆‍♀️ គ្រប់គ្រងសេវាកម្ម")
        col_srv_list, col_srv_add = st.columns([1.2, 1])
        with col_srv_list:
            if services_list:
                for s in services_list:
                    sc1, sc2 = st.columns([3, 1])
                    sc1.write(f"• **{s['name']}** - `${s['price']:.2f}`" + (f" ({s['desc']})" if s['desc'] else ""))
                    if sc2.button("🗑️ លុប", key=f"del_srv_{s['row_index']}"):
                        requests.post(APPS_SCRIPT_URL, json={"action": "delete_service", "row_index": s['row_index']}, timeout=20)
                        st.cache_data.clear()
                        st.rerun()
        with col_srv_add:
            with st.form("add_service_admin", clear_on_submit=True):
                s_name = st.text_input("ឈ្មោះសេវាកម្ម*")
                s_price = st.number_input("តម្លៃសេវាកម្ម ($)*", min_value=0.0, step=1.0)
                s_desc = st.text_input("ការពិពណ៌នាខ្លីៗ")
                if st.form_submit_button("➕ រក្សាទុកសេវាកម្ម"):
                    if s_name.strip():
                        requests.post(APPS_SCRIPT_URL, json={"action": "add_service", "name": s_name.strip(), "price": s_price, "desc": s_desc.strip()}, timeout=20)
                        st.cache_data.clear()
                        st.rerun()

    # PRODUCTS
    with ad_tab2:
        st.subheader("🛍️ គ្រប់គ្រងផលិតផល")
        col_prod_list, col_prod_add = st.columns([1.2, 1])
        with col_prod_list:
            if products_list:
                for p in products_list:
                    pc1, pc2 = st.columns([3, 1])
                    pc1.write(f"• **{p['name']}** - `${p['price']:.2f}` (ស្តុក: {p['stock']})")
                    if pc2.button("🗑️ លុប", key=f"del_prod_{p['row_index']}"):
                        requests.post(APPS_SCRIPT_URL, json={"action": "delete_product", "row_index": p['row_index']}, timeout=20)
                        st.cache_data.clear()
                        st.rerun()
        with col_prod_add:
            with st.form("add_product_admin", clear_on_submit=True):
                pn = st.text_input("ឈ្មោះផលិតផល*")
                pp = st.number_input("តម្លៃ ($)*", min_value=0.0, step=0.5)
                pi = st.text_input("Link រូបភាព", value=DEFAULT_PRODUCT_IMG)
                ps = st.number_input("ចំនួនក្នុងស្តុក*", min_value=0, value=10)
                pd_desc = st.text_input("ការពិពណ៌នា")
                if st.form_submit_button("➕ រក្សាទុកផលិតផល"):
                    if pn.strip():
                        requests.post(APPS_SCRIPT_URL, json={"action": "add_product", "name": pn.strip(), "price": pp, "image_url": pi, "stock": ps, "desc": pd_desc.strip()}, timeout=20)
                        st.cache_data.clear()
                        st.rerun()

    # PROMO CODES
    with ad_tab_promo:
        st.subheader("🎟️ បន្ថែម Promo Code")
        with st.form("add_promo_form", clear_on_submit=True):
            p_code = st.text_input("Promo Code (ឧ. DISCOUNT5)*").upper()
            p_disc = st.number_input("ចំនួនបញ្ចុះតម្លៃ ($)*", min_value=0.5, step=0.5)
            if st.form_submit_button("➕ បន្ថែម Promo Code"):
                if p_code.strip():
                    requests.post(APPS_SCRIPT_URL, json={"action": "add_promo", "code": p_code.strip(), "discount": p_disc}, timeout=20)
                    st.success("បានបន្ថែម Promo Code!")
                    st.cache_data.clear()
                    st.rerun()

    # ANALYTICS
    with ad_tab3:
        st.subheader("📊 ផ្ទាំងវិភាគចំណូល & ពិន្ទុ")
        if not df_bookings.empty:
            completed_df = df_bookings[df_bookings["Status"] == "Completed"]
            m1, m2, m3 = st.columns(3)
            m1.metric("ចំណូលសរុប (Completed)", f"${completed_df['Total Price'].sum():.2f}")
            m2.metric("ពិន្ទុបានផ្តល់សរុប", f"{df_bookings['Points Earned'].sum()} Pts")
            m3.metric("ពិន្ទុដែលបានប្រើយករង្វាន់", f"{df_bookings['Points Redeemed'].sum()} Pts")

    # SETTINGS
    with ad_tab5:
        st.subheader("⚙️ ការកំណត់ប្រព័ន្ធ & លក្ខខណ្ឌពិន្ទុ")
        with st.form("settings_admin"):
            set_threshold = st.number_input("កម្រិតកំណត់ស្តុកជិតអស់ (Low Stock Alert):", min_value=1, value=LOW_STOCK_THRESHOLD)
            st.markdown("---")
            set_pts_per_dollar = st.number_input("ចំនួនពិន្ទុទទួលបានលើការចំណាយ $1.00:", min_value=0.1, value=POINTS_PER_DOLLAR, step=0.5)
            set_pts_redeem_rate = st.number_input("ចំនួនពិន្ទុដែលត្រូវប្រើដើម្បីបាន $1.00 បញ្ចុះតម្លៃ:", min_value=1.0, value=POINTS_REDEEM_RATE, step=1.0)

            if st.form_submit_button("💾 រក្សាទុកការកំណត់"):
                requests.post(APPS_SCRIPT_URL, json={
                    "action": "update_settings",
                    "settings": {
                        "low_stock_threshold": str(set_threshold),
                        "points_per_dollar": str(set_pts_per_dollar),
                        "points_redeem_rate": str(set_pts_redeem_rate)
                    }
                }, timeout=20)
                st.success("✅ បានរក្សាទុកការកំណត់ជោគជ័យ!")
                st.cache_data.clear()
                st.rerun()
