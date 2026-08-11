import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time, timedelta

# ----------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# ----------------------------------------------------------------
st.set_page_config(
    page_title="អូនឡែន សម្រស់",
    page_icon="💇‍♀️",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 15px;
        color: white;
        border-left: 5px solid #3b82f6;
    }
    .receipt-card {
        background-color: #ffffff;
        color: #000000;
        padding: 20px;
        border-radius: 8px;
        border: 2px dashed #94a3b8;
        font-family: 'Courier New', Courier, monospace;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. Config & Secrets Management
# ----------------------------------------------------------------
APPS_SCRIPT_URL = st.secrets.get("APPS_SCRIPT_URL", "https://script.google.com/macros/s/AKfycbwlwyd3zHFO-9EzByegad9As7ti6KgwN-dLuZJl-219t6Ez97jpC_wjWMhpUkmWtGhw/exec")
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "123456")
DEFAULT_PRODUCT_IMG = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500"

def get_cambodia_now():
    """គណនាម៉ោងបច្ចុប្បន្ននៅប្រទេសកម្ពុជា (UTC+7)"""
    return datetime.utcnow() + timedelta(hours=7)

# ----------------------------------------------------------------
# 3. Helper Functions
# ----------------------------------------------------------------
def send_telegram_alert(msg_text):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg_text, "parse_mode": "Markdown"}, timeout=10)
        except Exception:
            pass

def calculate_vip_tier(phone, df_bookings):
    if df_bookings.empty or not phone.strip():
        return {"tier": "Standard", "discount": 0.0, "total_spent": 0.0, "total_bookings": 0}
    
    user_b = df_bookings[(df_bookings["Phone"].str.contains(phone.strip())) & (df_bookings["Status"] != "Cancelled")]
    total_spent = user_b["Total Price"].sum()
    total_bookings = len(user_b)

    if total_spent >= 300 or total_bookings >= 10:
        return {"tier": "VIP Gold", "discount": 15.0, "total_spent": total_spent, "total_bookings": total_bookings}
    elif total_spent >= 150 or total_bookings >= 5:
        return {"tier": "VIP Silver", "discount": 10.0, "total_spent": total_spent, "total_bookings": total_bookings}
    elif total_spent >= 50 or total_bookings >= 2:
        return {"tier": "Member", "discount": 5.0, "total_spent": total_spent, "total_bookings": total_bookings}
    else:
        return {"tier": "Standard", "discount": 0.0, "total_spent": total_spent, "total_bookings": total_bookings}

# ----------------------------------------------------------------
# 4. Load Data & Settings
# ----------------------------------------------------------------
@st.cache_data(ttl=5)
def load_all_data():
    try:
        res = requests.get(APPS_SCRIPT_URL, timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"bookings": [], "services": [], "blocked_dates": [], "products": [], "promo_codes": [], "reviews": [], "settings": []}

data = load_all_data()

# Settings
settings_dict = {"low_stock_threshold": 5}
if len(data.get("settings", [])) > 1:
    for r in data["settings"][1:]:
        if len(r) >= 2:
            settings_dict[str(r[0])] = str(r[1])

LOW_STOCK_THRESHOLD = int(settings_dict.get("low_stock_threshold", 5))

# Services Dict
services_dict = {}
if len(data.get("services", [])) > 1:
    for r in data["services"][1:]:
        if len(r) >= 2:
            try:
                services_dict[str(r[0])] = float(r[1])
            except Exception:
                pass

# Products List
products_list = []
low_stock_items = []
if len(data.get("products", [])) > 1:
    for idx, r in enumerate(data["products"][1:]):
        row = list(r) + [""] * (5 - len(r))
        try:
            stk = int(row[3]) if str(row[3]).isdigit() else 10
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
        except Exception:
            pass

# Promo Codes
promo_dict = {}
if len(data.get("promo_codes", [])) > 1:
    for r in data["promo_codes"][1:]:
        if len(r) >= 3 and str(r[2]).strip().lower() == "active":
            try:
                promo_dict[str(r[0]).strip().upper()] = float(r[1])
            except Exception:
                pass

# Bookings Dataframe
bookings_raw = data.get("bookings", [])
df_bookings = pd.DataFrame()
if len(bookings_raw) > 1:
    b_rows = []
    for idx, r in enumerate(bookings_raw[1:]):
        row = list(r) + [""] * (15 - len(r))
        try:
            b_rows.append({
                "sheet_row": idx + 2,
                "Created At": str(row[0]),
                "Customer Name": str(row[1]),
                "Phone": str(row[2]),
                "Services": str(row[3]),
                "Staff": str(row[4]),
                "Date": str(row[5]).split("T")[0],
                "Time": str(row[6]),
                "Note": str(row[7]),
                "Status": str(row[8]) if row[8] else "Pending",
                "Total Price": float(row[9]) if row[9] != "" else 0.0,
                "Deposit": str(row[10]),
                "Products": str(row[11]),
                "Promo": str(row[12]),
                "Discount": float(row[13]) if row[13] != "" else 0.0,
                "VIP_Tier": str(row[14]) if row[14] else "Standard"
            })
        except Exception:
            pass
    df_bookings = pd.DataFrame(b_rows)

# Reviews List
reviews_list = []
if len(data.get("reviews", [])) > 1:
    for idx, r in enumerate(data["reviews"][1:]):
        row = list(r) + [""] * (5 - len(r))
        try:
            reviews_list.append({
                "row_index": idx + 2,
                "date": str(row[0]).split("T")[0],
                "name": str(row[1]),
                "phone": str(row[2]),
                "rating": int(row[3]) if str(row[3]).isdigit() else 5,
                "comment": str(row[4])
            })
        except Exception:
            pass

# Blocked Dates
blocked_dates_dict = {}
if len(data.get("blocked_dates", [])) > 1:
    for r in data["blocked_dates"][1:]:
        if len(r) >= 1:
            d = str(r[0]).split("T")[0]
            blocked_dates_dict[d] = r[1] if len(r) > 1 else "ថ្ងៃសម្រាក"

# ----------------------------------------------------------------
# 5. Application Navigation
# ----------------------------------------------------------------
mode = st.query_params.get("mode", "client")
st.title("💇‍♀️ អូនឡែន សម្រស់")

# =================================================================
# 📱 1. CLIENT VIEW (?mode=client)
# =================================================================
if mode == "client":
    tab_c1, tab_c2, tab_c3 = st.tabs([
        "📝 កក់ម៉ោង & ទិញទំនិញ (Book & Shop)",
        "🔍 ពិនិត្យមើលការកក់ & វិក្កយបត្រ (Receipt)",
        "⭐️ មតិរិះគន់ & ការវាយតម្លៃ (Reviews)"
    ])

    with tab_c1:
        st.subheader("👤 1. ព័ត៌មានអតិថិជន & កម្រិតសមាជិក (Customer & VIP)")
        c1, c2 = st.columns(2)
        cust_name = c1.text_input("ឈ្មោះអតិថិជន / Name*")
        cust_phone = c2.text_input("លេខទូរស័ព្ទ / Phone*")

        vip_info = calculate_vip_tier(cust_phone, df_bookings)
        if cust_phone.strip():
            st.markdown(f"""
            <div class="metric-card">
                👑 <b>កម្រិតសមាជិកភាព: <span style="color:#f59e0b;">{vip_info['tier']}</span></b> 
                | ចំណាយសរុប: <b>${vip_info['total_spent']:.2f}</b> 
                | កក់បាន: <b>{vip_info['total_bookings']} ដង</b> 
                | ការបញ្ចុះតម្លៃសមាជិកស្វ័យប្រវត្តិ: <b>{vip_info['discount']:.0f}%</b>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("💆‍♀️ 2. ជ្រើសរើសសេវាកម្ម (Services)")
        sel_services = []
        if services_dict:
            service_display_options = [f"{name} (${price:.2f})" for name, price in services_dict.items()]
            service_map = {f"{name} (${price:.2f})": name for name, price in services_dict.items()}

            try:
                selected_pills = st.pills(
                    "👇 ចុចលើបូតុងសេវាកម្មខាងក្រោមដើម្បីជ្រើសរើស៖",
                    options=service_display_options,
                    selection_mode="multi"
                )
                sel_services = [service_map[item] for item in selected_pills] if selected_pills else []
            except AttributeError:
                cols = st.columns(2)
                for i, (s_name, s_price) in enumerate(services_dict.items()):
                    col = cols[i % 2]
                    is_selected = col.checkbox(f"✨ {s_name} — **${s_price:.2f}**", key=f"srv_{i}")
                    if is_selected:
                        sel_services.append(s_name)

        services_total = sum(services_dict.get(s, 0.0) for s in sel_services)

        st.markdown("---")
        st.subheader("🛍️ 3. ទំនិញថែរក្សាសម្រស់ (Products Catalog)")
        selected_products = {}
        ordered_items_list = []
        products_total = 0.0

        if products_list:
            p_cols = st.columns(3)
            for i, prod in enumerate(products_list):
                col = p_cols[i % 3]
                with col:
                    st.image(prod["image_url"], caption=f"{prod['name']} - ${prod['price']:.2f}", use_container_width=True)
                    st.caption(f"📦 ស្តុក: {prod['stock']} | {prod['desc']}")
                    qty = st.number_input(f"ចំនួន ({prod['name']}):", min_value=0, max_value=prod['stock'], key=f"p_qty_{i}")
                    if qty > 0:
                        selected_products[prod['name']] = {"price": prod['price'], "qty": qty}
                        ordered_items_list.append({"name": prod['name'], "qty": qty})
                        products_total += prod['price'] * qty

        st.markdown("---")
        st.subheader("⏰ 4. កាលបរិច្ឆេទ & ជាង (Date & Staff)")
        d1, d2, d3 = st.columns(3)
        staff = d1.selectbox("ជ្រើសរើសជាង / Staff:", ["អ្នកគ្រូ ឡែន"])
        
        # ប្រើប្រាស់ Timezone ប្រទេសកម្ពុជា
        cambodia_today = get_cambodia_now().date()
        book_date = d2.date_input("ថ្ងៃណាត់ជួប / Date:", cambodia_today)
        book_date_str = str(book_date)

        is_blocked = book_date_str in blocked_dates_dict
        all_slots = [time(h, m).strftime("%I:%M %p") for h in range(8, 21) for m in (0, 30)]
        booked_slots = df_bookings[(df_bookings["Date"] == book_date_str) & (df_bookings["Status"] != "Cancelled")]["Time"].tolist() if not df_bookings.empty else []
        avail_slots = [s for s in all_slots if s not in booked_slots]

        if is_blocked:
            d3.error(f"❌ ហាងបិទសម្រាក ({blocked_dates_dict[book_date_str]})")
            book_time = None
        elif avail_slots:
            book_time = d3.selectbox("ម៉ោងទំនេរ / Time Slot:", avail_slots)
        else:
            d3.warning("❌ ពេញម៉ោងអស់ហើយ!")
            book_time = None

        st.markdown("---")
        st.subheader("💳 5. គណនាប្រាក់សរុប (Payment Calculation)")
        p_col1, p_col2 = st.columns(2)
        input_promo = p_col1.text_input("បញ្ចូល Promo Code (ប្រសិនបើមាន):").strip().upper()

        promo_discount = promo_dict.get(input_promo, 0.0)
        vip_discount = vip_info['discount']
        total_discount_percent = max(promo_discount, vip_discount)

        subtotal = services_total + products_total
        discount_val = (subtotal * total_discount_percent) / 100.0
        final_total = subtotal - discount_val

        p_col1.markdown(f"""
            * ការបញ្ចុះតម្លៃ Promo Code: **{promo_discount:.0f}%**
            * ការបញ្ចុះតម្លៃ VIP Member: **{vip_discount:.0f}%**
            * ភាគរយចុះតម្លៃអនុវត្តសរុប: <b style="color:green;">{total_discount_percent:.0f}%</b>
        """, unsafe_allow_html=True)

        p_col2.markdown(f"""
            ### 💰 ចំនួនត្រូវទូទាត់សរុប: <span style="color:#2563eb;">${final_total:.2f}</span>
        """, unsafe_allow_html=True)

        if st.button("✅ បញ្ជាក់ការកក់ & ចេញវិក្កយបត្រ", type="primary", use_container_width=True):
            if not cust_name.strip() or not cust_phone.strip():
                st.error("❌ សូមបញ្ចូលឈ្មោះ និងលេខទូរស័ព្ទ!")
            elif not sel_services and not selected_products:
                st.error("❌ សូមជ្រើសរើសសេវាកម្ម ឬទំនិញយ៉ាងហោចណាស់មួយ!")
            elif is_blocked or not book_time:
                st.error("❌ មិនអាចកក់បានទេ!")
            else:
                prod_str = ", ".join([f"{k} (x{v['qty']})" for k, v in selected_products.items()]) if selected_products else "None"
                payload = {
                    "action": "add_booking",
                    "customer_name": cust_name.strip(),
                    "phone": cust_phone.strip(),
                    "service": ", ".join(sel_services),
                    "staff": staff,
                    "date": book_date_str,
                    "time": book_time,
                    "note": "",
                    "status": "Pending",
                    "total_price": final_total,
                    "deposit": "None",
                    "products_ordered": prod_str,
                    "promo_code": input_promo if input_promo else "None",
                    "discount_amount": discount_val,
                    "vip_tier": vip_info['tier'],
                    "ordered_items_list": ordered_items_list
                }
                
                try:
                    with st.spinner("⏳ កំពុងរក្សាទុកទិន្នន័យការកក់..."):
                        response = requests.post(APPS_SCRIPT_URL, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        alert_msg = (
                            f"🔔 *ការកក់ម៉ោង & កម្ម៉ង់ទំនិញថ្មី!*\n\n"
                            f"👤 *អតិថិជន:* {cust_name.strip()} ({vip_info['tier']})\n"
                            f"📞 *ទូរស័ព្ទ:* `{cust_phone.strip()}`\n"
                            f"💆‍♀️ *សេវាកម្ម:* {', '.join(sel_services)}\n"
                            f"🛍️ *ទំនិញ:* {prod_str}\n"
                            f"📅 *ថ្ងៃណាត់:* {book_date_str} | 🕒 *ម៉ោង:* {book_time}\n"
                            f"💰 *សរុបទូទាត់:* ${final_total:.2f}"
                        )
                        send_telegram_alert(alert_msg)

                        st.balloons()
                        st.success("🎉 ការកក់ជោគជ័យ! លោកអ្នកអាចពិនិត្យវិក្កយបត្រក្នុង Tab ទី ២។")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ មានបញ្ហាក្នុងការរក្សាទុកទិន្នន័យ!")
                except Exception as e:
                    st.error(f"❌ កើតមានកំហុស៖ {e}")

    # Tab 2: Digital Receipt
    with tab_c2:
        st.subheader("🔍 ស្វែងរកការកក់ & បោះពុម្ពវិក្កយបត្រ (Digital Receipt)")
        s_phone = st.text_input("បញ្ចូលលេខទូរស័ព្ទដើម្បីមើលវិក្កយបត្រ:")
        if s_phone.strip() and not df_bookings.empty:
            res_df = df_bookings[df_bookings["Phone"].str.contains(s_phone.strip())]
            if not res_df.empty:
                for _, r in res_df.iterrows():
                    st.markdown(f"""
                    <div class="receipt-card">
                        <h3 style="text-align:center; margin:0;">🧾 OUNLEN BEAUTY SALON</h3>
                        <p style="text-align:center; font-size:12px; margin-bottom:15px;">Kampong Chhnang | Tel: 012 345 678</p>
                        <hr>
                        <p><b>កាលបរិច្ឆេទ:</b> {r['Created At']}</p>
                        <p><b>អតិថិជន:</b> {r['Customer Name']} ({r['VIP_Tier']})</p>
                        <p><b>លេខទូរស័ព្ទ:</b> {r['Phone']}</p>
                        <p><b>ថ្ងៃណាត់ធ្វើ:</b> {r['Date']} @ {r['Time']}</p>
                        <p><b>ជាងទទួលបន្ទុក:</b> {r['Staff']}</p>
                        <hr>
                        <p><b>សេវាកម្ម:</b> {r['Services']}</p>
                        <p><b>ទំនិញទិញបន្ថែម:</b> {r['Products']}</p>
                        <p><b>បញ្ចុះតម្លៃ:</b> -${r['Discount']:.2f}</p>
                        <h3 style="text-align:right;">សរុប: ${r['Total Price']:.2f}</h3>
                        <p style="text-align:center; font-size:11px;">Status: <b>{r['Status']}</b> | អរគុណសម្រាប់ការគាំទ្រ!</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

    # Tab 3: Reviews System
    with tab_c3:
        st.subheader("⭐️ ស្ទង់មតិ & ការវាយតម្លៃពីអតិថិជន")
        if reviews_list:
            avg_rating = sum(r['rating'] for r in reviews_list) / len(reviews_list)
            st.metric("ពិន្ទុវាយតម្លៃមធ្យម", f"⭐️ {avg_rating:.1f} / 5.0", f"ពីការវាយតម្លៃ {len(reviews_list)} មតិ")

        st.markdown("---")
        rev_name = st.text_input("ឈ្មោះរបស់អ្នក:")
        rev_phone = st.text_input("លេខទូរស័ព្ទ:")
        rev_star = st.slider("ផ្តល់ពិន្ទុ (Stars):", 1, 5, 5)
        rev_comment = st.text_area("មតិរិះគន់ ឬការសរសើរ:")

        if st.button("📤 ផ្ញើការវាយតម្លៃ", type="primary"):
            if rev_name.strip() and rev_comment.strip():
                try:
                    requests.post(APPS_SCRIPT_URL, json={
                        "action": "add_review",
                        "customer_name": rev_name.strip(),
                        "phone": rev_phone.strip(),
                        "rating": rev_star,
                        "comment": rev_comment.strip()
                    }, timeout=20)
                    st.success("✅ អរគុណសម្រាប់ការផ្តល់មតិវាយតម្លៃ!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ កើតមានកំហុស៖ {e}")

# =================================================================
# 👑 2. ADMIN DASHBOARD (?mode=admin)
# =================================================================
elif mode == "admin":
    st.title("👑 ម្ចាស់ហាង អូនឡែន សម្រស់")

    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        pwd = st.text_input("បញ្ចូលពាក្យសម្ងាត់ Admin Password:", type="password")
        if st.button("🔑 ចូលប្រព័ន្ធ"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("❌ ពាក្យសម្ងាត់មិនត្រឹមត្រូវ!")
        st.stop()

    if low_stock_items:
        st.warning(f"⚠️ **ផលិតផលជិតអស់ពីស្តុក (សល់ ≤ {LOW_STOCK_THRESHOLD}):** " + 
                   ", ".join([f"{item['name']} (សល់ {item['stock']})" for item in low_stock_items]))

    ad_tab1, ad_tab2, ad_tab3, ad_tab4, ad_tab5, ad_tab6 = st.tabs([
        "📋 ការកក់ (Bookings)",
        "🛍️ ផលិតផល & ស្តុក",
        "📊 វិភាគទិន្នន័យ (Analytics)",
        "👑 VIP & Promo",
        "⭐️ មតិរិះគន់",
        "⚙️ កំណត់ប្រព័ន្ធ"
    ])

    with ad_tab1:
        st.subheader("📋 គ្រប់គ្រងការកក់")
        if not df_bookings.empty:
            st.dataframe(df_bookings[["sheet_row", "Customer Name", "Phone", "Services", "Products", "Date", "Time", "Total Price", "Status", "VIP_Tier"]], use_container_width=True)
            sel_row = st.selectbox("ជ្រើសរើស Row ID ដើម្បីប្តូរ Status:", df_bookings["sheet_row"].tolist())
            c_s1, c_s2, c_s3 = st.columns(3)
            if c_s1.button("🟢 Confirm"):
                requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": sel_row, "status": "Confirmed"}, timeout=20)
                st.cache_data.clear()
                st.rerun()
            if c_s2.button("🔵 Complete"):
                requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": sel_row, "status": "Completed"}, timeout=20)
                st.cache_data.clear()
                st.rerun()
            if c_s3.button("🔴 Cancel"):
                requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": sel_row, "status": "Cancelled"}, timeout=20)
                st.cache_data.clear()
                st.rerun()

    with ad_tab2:
        st.subheader("➕ បន្ថែមផលិតផលថ្មី")
        with st.form("add_prod_form", clear_on_submit=True):
            pn = st.text_input("ឈ្មោះផលិតផល*")
            pp = st.number_input("តម្លៃ ($)*", min_value=0.0, step=0.5)
            pi = st.text_input("Link រូបភាព", value=DEFAULT_PRODUCT_IMG)
            ps = st.number_input("ចំនួនក្នុងស្តុក*", min_value=0, value=10)
            pd_desc = st.text_input("ការពិពណ៌នា")
            if st.form_submit_button("➕ រក្សាទុក"):
                requests.post(APPS_SCRIPT_URL, json={"action": "add_product", "name": pn, "price": pp, "image_url": pi, "stock": ps, "desc": pd_desc}, timeout=20)
                st.success("បានបន្ថែម!")
                st.cache_data.clear()
                st.rerun()

        st.markdown("---")
        for p in products_list:
            col1, col2, col3 = st.columns([1, 4, 1])
            col1.image(p["image_url"], width=60)
            col2.write(f"**{p['name']}** | តម្លៃ: `${p['price']:.2f}` | ស្តុក: `{p['stock']}`")
            if col3.button("🗑️ លុប", key=f"del_{p['row_index']}"):
                requests.post(APPS_SCRIPT_URL, json={"action": "delete_product", "row_index": p['row_index']}, timeout=20)
                st.cache_data.clear()
                st.rerun()

    with ad_tab3:
        st.subheader("📊 ផ្ទាំងវិភាគចំណូល")
        if not df_bookings.empty:
            completed_df = df_bookings[df_bookings["Status"] == "Completed"]
            m1, m2, m3 = st.columns(3)
            m1.metric("ចំណូលសរុប (Completed)", f"${completed_df['Total Price'].sum():.2f}")
            m2.metric("ការកក់ជោគជ័យសរុប", f"{len(completed_df)} ដង")
            m3.metric("ការកក់ Pending", f"{len(df_bookings[df_bookings['Status'] == 'Pending'])} ដង")

    with ad_tab4:
        st.subheader("🎟️ បង្កើត Promo Code")
        with st.form("add_promo_form", clear_on_submit=True):
            code = st.text_input("កូដបញ្ចុះតម្លៃ*").strip().upper()
            disc = st.number_input("ភាគរយចុះ (%)*", min_value=1.0, max_value=100.0, value=10.0)
            if st.form_submit_button("➕ បន្ថែម Promo"):
                requests.post(APPS_SCRIPT_URL, json={"action": "add_promo", "code": code, "discount": disc}, timeout=20)
                st.success("បានបន្ថែម!")
                st.cache_data.clear()

    with ad_tab5:
        st.subheader("⭐️ គ្រប់គ្រងការវាយតម្លៃ")
        for rev in reviews_list:
            r_col1, r_col2 = st.columns([5, 1])
            r_col1.write(f"**{rev['name']}** - {'⭐' * rev['rating']} - *{rev['comment']}*")
            if r_col2.button("🗑️ លុប", key=f"del_rev_{rev['row_index']}"):
                requests.post(APPS_SCRIPT_URL, json={"action": "delete_review", "row_index": rev['row_index']}, timeout=20)
                st.cache_data.clear()
                st.rerun()

    with ad_tab6:
        st.subheader("⚙️ ការកំណត់ប្រព័ន្ធ")
        with st.form("settings_form"):
            set_threshold = st.number_input("កម្រិតកំណត់ស្តុកជិតអស់:", value=LOW_STOCK_THRESHOLD)
            if st.form_submit_button("💾 រក្សាទុក"):
                payload = {"action": "update_settings", "settings": {"low_stock_threshold": str(set_threshold)}}
                requests.post(APPS_SCRIPT_URL, json=payload, timeout=20)
                st.success("✅ បានរក្សាទុក!")
                st.cache_data.clear()
                st.rerun()
