import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, time

# ----------------------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen Salon & Retail Hub",
    page_icon="💇‍♀️",
    layout="wide"
)

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwlwyd3zHFO-9EzByegad9As7ti6KgwN-dLuZJl-219t6Ez97jpC_wjWMhpUkmWtGhw/exec"

TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", "8802043451:AAEAp35949z9IQLa5kj6Ecl75Q5uzIv-F_4")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "-1004491712284")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "123456")

DEFAULT_PRODUCT_IMG = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500"

# ----------------------------------------------------------------
# 2. Language Switcher State
# ----------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "KM"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "KM" else "KM"

# ----------------------------------------------------------------
# 3. Helper Functions
# ----------------------------------------------------------------
def send_telegram_alert(name, phone, services, products, date_str, time_str, total, promo):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        msg = (
            f"🔔 *ការកក់ម៉ោង & កម្ម៉ង់ទំនិញថ្មី!*\n\n"
            f"👤 *អតិថិជន:* {name}\n"
            f"📞 *ទូរស័ព្ទ:* `{phone}`\n"
            f"💆‍♀️ *សេវាកម្ម:* {services}\n"
            f"🛍️ *ទំនិញទិញបន្ថែម:* {products}\n"
            f"🎟️ *Promo Code:* {promo}\n"
            f"📅 *ថ្ងៃណាត់:* {date_str} | 🕒 *ម៉ោង:* {time_str}\n"
            f"💰 *តម្លៃសរុបចុងក្រោយ:* ${total:.2f}"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=5)
        except Exception:
            pass

def clean_str(val):
    return str(val).strip() if val else ""

# ----------------------------------------------------------------
# 4. Data Loading
# ----------------------------------------------------------------
@st.cache_data(ttl=3)
def load_all_data():
    try:
        res = requests.get(APPS_SCRIPT_URL, timeout=8)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"bookings": [], "services": [], "blocked_dates": [], "products": [], "promo_codes": []}

data = load_all_data()

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
if len(data.get("products", [])) > 1:
    for idx, r in enumerate(data["products"][1:]):
        row = list(r) + [""] * (5 - len(r))
        try:
            products_list.append({
                "row_index": idx + 2,
                "name": str(row[0]),
                "price": float(row[1]) if row[1] != "" else 0.0,
                "image_url": str(row[2]) if row[2] else DEFAULT_PRODUCT_IMG,
                "stock": int(row[3]) if str(row[3]).isdigit() else 10,
                "desc": str(row[4])
            })
        except Exception:
            pass

# Promo Codes Dict {code: discount_percent}
promo_dict = {}
if len(data.get("promo_codes", [])) > 1:
    for r in data["promo_codes"][1:]:
        if len(r) >= 3 and str(r[2]).strip().lower() == "active":
            try:
                promo_dict[str(r[0]).strip().upper()] = float(r[1])
            except Exception:
                pass

# Blocked Dates Dict
blocked_dates_dict = {}
if len(data.get("blocked_dates", [])) > 1:
    for r in data["blocked_dates"][1:]:
        if len(r) >= 1:
            d = str(r[0]).split("T")[0]
            blocked_dates_dict[d] = r[1] if len(r) > 1 else "ថ្ងៃសម្រាក"

# Bookings Dataframe
bookings_raw = data.get("bookings", [])
df_bookings = pd.DataFrame()
if len(bookings_raw) > 1:
    b_rows = []
    for idx, r in enumerate(bookings_raw[1:]):
        row = list(r) + [""] * (14 - len(r))
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
                "Discount": float(row[13]) if row[13] != "" else 0.0
            })
        except Exception:
            pass
    df_bookings = pd.DataFrame(b_rows)

# ----------------------------------------------------------------
# 5. UI Layout & Navigation
# ----------------------------------------------------------------
lang = st.session_state.lang
mode = st.query_params.get("mode", "client")

# Header Bar
col_h1, col_h2 = st.columns([8, 2])
with col_h1:
    st.title("💇‍♀️ OunLen Beauty & Retail Hub")
with col_h2:
    if st.button(f"🌐 ភាសា/Lang: {'ខ្មែរ' if lang == 'KM' else 'English'}"):
        toggle_language()
        st.rerun()

# =================================================================
# 📱 1. CLIENT VIEW (?mode=client)
# =================================================================
if mode == "client":
    tab_c1, tab_c2 = st.tabs([
        "📝 កក់ម៉ោង & ទិញទំនិញ (Book & Shop)" if lang == "KM" else "📝 Book & Shop",
        "🔍 ពិនិត្យមើលការកក់ (Check Booking)" if lang == "KM" else "🔍 Check Booking"
    ])

    with tab_c1:
        st.subheader("👤 1. ព័ត៌មានអតិថិជន (Customer Info)")
        c1, c2 = st.columns(2)
        cust_name = c1.text_input("ឈ្មោះអតិថិជន / Name*")
        cust_phone = c2.text_input("លេខទូរស័ព្ទ / Phone*")

        # Loyalty Point Check
        if cust_phone.strip() and not df_bookings.empty:
            user_b = df_bookings[df_bookings["Phone"].str.contains(cust_phone.strip())]
            pts = len(user_b)
            st.info(f"🎁 ប្រព័ន្ធសន្សំពិន្ទុ (Loyalty): លេខ `{cust_phone}` មាន **{pts} ពិន្ទុ** (កក់បាន {pts} ដង)")

        st.markdown("---")
        st.subheader("💆‍♀️ 2. ជ្រើសរើសសេវាកម្ម (Select Services)")
        sel_services = st.multiselect(
            "សេវាកម្ម (អាចជ្រើសបានច្រើន):",
            options=list(services_dict.keys()),
            default=[list(services_dict.keys())[0]] if services_dict else []
        )
        services_total = sum(services_dict.get(s, 0.0) for s in sel_services)

        st.markdown("---")
        st.subheader("🛍️ 3. ទំនិញថែរក្សាសម្រស់ (Beauty Products Catalog)")
        selected_products = {}
        products_total = 0.0

        if products_list:
            p_cols = st.columns(3)
            for i, prod in enumerate(products_list):
                col = p_cols[i % 3]
                with col:
                    st.image(prod["image_url"], caption=f"{prod['name']} - ${prod['price']:.2f}", use_container_width=True)
                    st.caption(f"📦 ស្តុកនៅសល់: {prod['stock']} | {prod['desc']}")
                    qty = st.number_input(f"ចំនួន ({prod['name']}):", min_value=0, max_value=prod['stock'], key=f"p_qty_{i}")
                    if qty > 0:
                        selected_products[prod['name']] = {"price": prod['price'], "qty": qty}
                        products_total += prod['price'] * qty
        else:
            st.info("មិនទាន់មានទិន្នន័យផលិតផលនៅឡើយទេ។")

        st.markdown("---")
        st.subheader("⏰ 4. កាលបរិច្ឆេទ & ជាង (Date & Staff)")
        d1, d2, d3 = st.columns(3)
        staff = d1.selectbox("ជ្រើសរើសជាង / Staff:", ["អ្នកគ្រូ ឡែន", "កញ្ញា ម៉ារី", "ចៃដន្យ (Any)"])
        book_date = d2.date_input("ថ្ងៃណាត់ជួប / Date:", datetime.now())
        book_date_str = str(book_date)

        is_blocked = book_date_str in blocked_dates_dict

        # Time Slots
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
        st.subheader("🎟️ 5. កូដបញ្ចុះតម្លៃ & ទូទាត់ (Promo Code & Payment)")
        p_col1, p_col2 = st.columns(2)
        input_promo = p_col1.text_input("បញ្ចូល Promo Code (ប្រសិនបើមាន):").strip().upper()
        
        discount_percent = 0.0
        if input_promo in promo_dict:
            discount_percent = promo_dict[input_promo]
            p_col1.success(f"🎉 ទទួលបានការបញ្ចុះតម្លៃ {discount_percent:.0f}%!")
        elif input_promo:
            p_col1.error("❌ កូដបញ្ចុះតម្លៃមិនត្រឹមត្រូវ!")

        subtotal = services_total + products_total
        discount_val = (subtotal * discount_percent) / 100.0
        final_total = subtotal - discount_val

        p_col2.markdown(f"""
            #### 💰 គិតប្រាក់សរុប:
            * សេវាកម្ម: **${services_total:.2f}**
            * ផលិតផល: **${products_total:.2f}**
            * បញ្ចុះតម្លៃ ({discount_percent:.0f}%): **-${discount_val:.2f}**
            ---
            ### 🔥 ចំនួនត្រូវទូទាត់សរុប: <span style="color:#2563eb;">${final_total:.2f}</span>
        """, unsafe_allow_html=True)

        st.info("💳 **ABA KHQR Deposit:** 000 123 456 (OunLen Salon) - ប្រាក់កក់ $2.00")
        dep_ref = st.text_input("លេខកូដប្រាក់កក់ ABA Reference Number (Optional):")

        if st.button("✅ បញ្ជាក់ការកក់ & កម្ម៉ង់ទំនិញ", type="primary", use_container_width=True):
            if not cust_name.strip() or not cust_phone.strip():
                st.error("❌ សូមបញ្ចូលឈ្មោះ និងលេខទូរស័ព្ទ!")
            elif not sel_services and not selected_products:
                st.error("❌ សូមជ្រើសរើសសេវាកម្ម ឬទំនិញយ៉ាងហោចណាស់មួយ!")
            elif is_blocked or not book_time:
                st.error("❌ មិនអាចកក់បានទេ ព្រោះហាងបិទ ឬអស់ម៉ោង!")
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
                    "deposit": dep_ref.strip(),
                    "products_ordered": prod_str,
                    "promo_code": input_promo if input_promo else "None",
                    "discount_amount": discount_val
                }
                res = requests.post(APPS_SCRIPT_URL, json=payload, timeout=10)
                send_telegram_alert(cust_name.strip(), cust_phone.strip(), ", ".join(sel_services), prod_str, book_date_str, book_time, final_total, input_promo)
                st.balloons()
                st.success("🎉 ការកក់ទទួលបានជោគជ័យ! យើងខ្ញុំនឹងទាក់ទងទៅផ្លូវការក្នុងពេលឆាប់ៗ។")
                st.cache_data.clear()

    # Tab Check Booking
    with tab_c2:
        st.subheader("🔍 ស្វែងរកការកក់តាមលេខទូរស័ព្ទ")
        s_phone = st.text_input("លេខទូរស័ព្ទរបស់អ្នក:")
        if s_phone.strip() and not df_bookings.empty:
            res_df = df_bookings[df_bookings["Phone"].str.contains(s_phone.strip())]
            if not res_df.empty:
                for _, r in res_df.iterrows():
                    st.markdown(f"""
                    <div style="background-color:#1e293b; color:white; padding:16px; border-radius:12px; margin-bottom:10px;">
                        <h4 style="color:#60a5fa; margin:0;">💆‍♀️ {r['Services']}</h4>
                        <p style="margin:4px 0;">📦 <b>ទំនិញ:</b> {r['Products']} | <b>📅 ថ្ងៃ:</b> {r['Date']} {r['Time']}</p>
                        <p style="margin:4px 0;">💰 <b>សរុប:</b> ${r['Total Price']:.2f} | <b>Status:</b> {r['Status']}</p>
                    </div>
                    """, unsafe_allow_html=True)

# =================================================================
# 👑 2. ADMIN DASHBOARD (?mode=admin)
# =================================================================
elif mode == "admin":
    st.title("👑 Admin Dashboard")

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

    ad_tab1, ad_tab2, ad_tab3, ad_tab4, ad_tab5 = st.tabs([
        "📋 ការកក់ (Bookings)", 
        "🛍️ ផលិតផល & រូបភាព (Products & Images)", 
        "🎟️ Promo Code", 
        "💰 ភាគរយជាង (Commission)", 
        "📊 Export ទិន្នន័យ (Export Data)"
    ])

    # Tab 1: Bookings Management
    with ad_tab1:
        st.subheader("📋 បញ្ជីការកក់ទាំងអស់")
        if not df_bookings.empty:
            st.dataframe(df_bookings[["sheet_row", "Customer Name", "Phone", "Services", "Products", "Date", "Time", "Total Price", "Status"]], use_container_width=True)
            
            st.markdown("---")
            st.subheader("⚙️ ធ្វើបច្ចុប្បន្នភាព Status")
            sel_row = st.selectbox("ជ្រើសរើស ID ជួរកក់ (Row):", df_bookings["sheet_row"].tolist())
            c_s1, c_s2, c_s3 = st.columns(3)
            if c_s1.button("🟢 Confirm"):
                requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": sel_row, "status": "Confirmed"})
                st.cache_data.clear()
                st.rerun()
            if c_s2.button("🔵 Complete"):
                requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": sel_row, "status": "Completed"})
                st.cache_data.clear()
                st.rerun()
            if c_s3.button("🔴 Cancel"):
                requests.post(APPS_SCRIPT_URL, json={"action": "update_status", "row_index": sel_row, "status": "Cancelled"})
                st.cache_data.clear()
                st.rerun()

    # Tab 2: Manage Products with Images
    with ad_tab2:
        st.subheader("➕ បន្ថែមផលិតផលថ្មីជាមួយរូបភាព (Product with Image)")
        with st.form("add_product_form", clear_on_submit=True):
            p_name = st.text_input("ឈ្មោះផលិតផល*")
            p_price = st.number_input("តម្លៃ ($)*", min_value=0.0, step=0.5)
            p_img = st.text_input("Link រូបភាពផលិតផល (Image URL)*", value=DEFAULT_PRODUCT_IMG)
            p_stock = st.number_input("ចំនួនក្នុងស្តុក*", min_value=1, value=20)
            p_desc = st.text_input("ការពិពណ៌នា (Description)")
            
            if st.form_submit_button("➕ បន្ថែមផលិតផល") and p_name.strip():
                payload = {
                    "action": "add_product",
                    "name": p_name.strip(),
                    "price": p_price,
                    "image_url": p_img.strip(),
                    "stock": p_stock,
                    "desc": p_desc.strip()
                }
                requests.post(APPS_SCRIPT_URL, json=payload, timeout=10)
                st.success("✅ បានបន្ថែមផលិតផលជោគជ័យ!")
                st.cache_data.clear()
                st.rerun()

        st.markdown("---")
        st.subheader("📦 បញ្ជីផលិតផលបច្ចុប្បន្ន")
        if products_list:
            for p in products_list:
                col_p1, col_p2, col_p3 = st.columns([1, 4, 1])
                col_p1.image(p["image_url"], width=80)
                col_p2.markdown(f"**{p['name']}** | តម្លៃ: `${p['price']:.2f}` | ស្តុក: `{p['stock']}`")
                if col_p3.button("🗑️ លុប", key=f"del_prod_{p['row_index']}"):
                    requests.post(APPS_SCRIPT_URL, json={"action": "delete_product", "row_index": p['row_index']})
                    st.success("បានលុប!")
                    st.cache_data.clear()
                    st.rerun()

    # Tab 3: Promo Codes
    with ad_tab3:
        st.subheader("🎟️ បង្កើត Promo Code បញ្ចុះតម្លៃ")
        with st.form("add_promo_form", clear_on_submit=True):
            pr_code = st.text_input("កូដបញ្ចុះតម្លៃ (ឧ. PROMO10)*").strip().upper()
            pr_disc = st.number_input("ភាគរយចុះតម្លៃ (%)*", min_value=1.0, max_value=100.0, value=10.0)
            if st.form_submit_button("➕ បន្ថែម កូដ Promo"):
                requests.post(APPS_SCRIPT_URL, json={"action": "add_promo", "code": pr_code, "discount": pr_disc})
                st.success(f"✅ បានបន្ថែម Promo `{pr_code}`!")
                st.cache_data.clear()

    # Tab 4: Staff Commission
    with ad_tab4:
        st.subheader("💰 គណនាកម្រៃជើងសារជាង (Staff Commission)")
        comm_rate = st.slider("ភាគរយកម្រៃជើងសារ (%)", min_value=5, max_value=50, value=10)
        if not df_bookings.empty:
            completed_df = df_bookings[df_bookings["Status"] == "Completed"]
            staff_summary = completed_df.groupby("Staff").agg(
                Total_Sales=('Total Price', 'sum'),
                Completed_Jobs=('Services', 'count')
            ).reset_index()
            staff_summary["Commission_Earned ($)"] = (staff_summary["Total_Sales"] * comm_rate) / 100.0
            st.dataframe(staff_summary, use_container_width=True)

    # Tab 5: Export Data
    with ad_tab5:
        st.subheader("📥 ទាញយកទិន្នន័យជា CSV/Excel (Export Reports)")
        if not df_bookings.empty:
            csv_data = df_bookings.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Bookings Data (CSV)",
                data=csv_data,
                file_name=f"bookings_report_{date.today()}.csv",
                mime="text/csv"
            )
