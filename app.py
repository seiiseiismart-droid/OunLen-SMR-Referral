import streamlit as st
import pandas as pd
import requests
import hashlib
from datetime import datetime

# ----------------------------------------------------------------
# 1. ការកំណត់ទំព័រ Streamlit
# ----------------------------------------------------------------
st.set_page_config(page_title="OunLen SMR - POS & Referral", page_icon="💇‍♀️", layout="wide")

# អត្រាប្ដូរប្រាក់ថេរ
EXCHANGE_RATE = 4050

# ----------------------------------------------------------------
# 2. ទាញយកព័ត៌មានពី Secrets & Caching
# ----------------------------------------------------------------
try:
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    SCRIPT_URL = st.secrets["connections"]["gsheets"]["script_url"]
    
    if "docs.google.com/spreadsheets" in spreadsheet_url:
        spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Referral"
    else:
        csv_url = spreadsheet_url

except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Secrets បានទេ! សូមពិនិត្យមើល `.streamlit/secrets.toml` ឡើងវិញ។")
    st.stop()

@st.cache_data(ttl=5)
def load_data(url):
    try:
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame()

raw_df = load_data(csv_url)

df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "រូបភាព", "ស្ថានភាព"])

if not raw_df.empty:
    raw_df.columns = [str(col).strip() for col in raw_df.columns]
    cols_count = len(raw_df.columns)
    
    if cols_count >= 6: 
        df["កូដកាត"] = raw_df.iloc[:, 1]
        df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 2]
        df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 3]
        df["រូបភាព"] = raw_df.iloc[:, 4]
        df["ស្ថានភាព"] = raw_df.iloc[:, 5]
    elif cols_count >= 5:
        df["កូដកាត"] = raw_df.iloc[:, 1]
        df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 2]
        df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 3]
        df["ស្ថានភាព"] = raw_df.iloc[:, 4]
        df["រូបភាព"] = ""

if not df.empty:
    df = df.dropna(subset=["កូដកាត"])
    df["កូដកាត"] = df["កូដកាត"].astype(str).str.strip().str.upper()

# ----------------------------------------------------------------
# 3. ប្រព័ន្ធ Authentication
# ----------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if not st.session_state.logged_in:
    st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងការលក់ និងគិតលុយ 🇰🇭")
    st.markdown("---")
    auth_tab1, auth_tab2 = st.tabs(["🔐 ចូលប្រើប្រាស់ (Login)", "📝 បង្កើតគណនីថ្មី (Sign Up)"])
    
    with auth_tab1:
        st.subheader("សូមបំពេញព័ត៌មានដើម្បីចូលប្រើប្រាស់")
        username = st.text_input("ឈ្មោះអ្នកប្រើប្រាស់ (Username)", key="login_user").strip()
        password = st.text_input("លេខកូដសម្ងាត់ (Password)", type="password", key="login_pass")
        
        if st.button("ចូលប្រើប្រាស់", type="primary", use_container_width=True):
            if username and password:
                hashed_password = make_hashes(password)
                params = {"action": "login", "username": username, "password": hashed_password}
                try:
                    with st.spinner("⏳ កំពុងផ្ទៀងផ្ទាត់..."):
                        response = requests.post(SCRIPT_URL, json=params)
                    if response.status_code == 200 and "success" in response.text.lower():
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("❌ ឈ្មោះអ្នកប្រើ ឬ លេខកូដសម្ងាត់មិនត្រឹមត្រូវទេ!")
                except Exception as req_err:
                    st.error(f"❌ មានបញ្ហាក្នុងការតភ្ជាប់! ({str(req_err)})")
            else:
                st.warning("⚠️ សូមបំពេញព័ត៌មានឱ្យបានគ្រប់គ្រាន់។")
                
    with auth_tab2:
        st.subheader("បង្កើតគណនីសម្រាប់បុគ្គលិកថ្មី")
        new_user = st.text_input("ឈ្មោះអ្នកប្រើប្រាស់ថ្មី (Username)", key="signup_user").strip()
        new_password = st.text_input("បង្កើតលេខកូដសម្ងាត់ (Password)", type="password", key="signup_pass")
        confirm_password = st.text_input("បញ្ជាក់លេខកូដសម្ងាត់ម្តងទៀត", type="password", key="signup_confirm")
        
        if st.button("ចុះឈ្មោះគណនី", use_container_width=True):
            if new_user and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("❌ លេខកូដសម្ងាត់ទាំងពីរមិនដូចគ្នាទេ!")
                else:
                    hashed_password = make_hashes(new_password)
                    params = {"action": "signup", "username": new_user, "password": hashed_password}
                    try:
                        with st.spinner("⏳ កំពុងបង្កើតគណនី..."):
                            response = requests.post(SCRIPT_URL, json=params)
                        if response.status_code == 200 and "success" in response.text.lower():
                            st.success("🎉 បង្កើតគណនីជោគជ័យ! សូមចូលប្រើប្រាស់។")
                        else:
                            st.error("❌ មិនអាចបង្កើតគណនីបានទេ!")
                    except:
                        st.error("❌ មានបញ្ហាក្នុងការតភ្ជាប់!")
            else:
                st.warning("⚠️ សូមបំពេញព័ត៌មានឱ្យបានគ្រប់គ្រាន់។")
    st.stop()

# ----------------------------------------------------------------
# 4. Sidebar & Cart Session Setup
# ----------------------------------------------------------------
st.sidebar.title("💇‍♀️ អូនឡែន សម្រស់")
st.sidebar.write(f"👤 អ្នកគិតលុយ៖ **{st.session_state.username}**")
if st.sidebar.button("🚪 ចាកចេញ (Logout)"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.cart = []
    st.cache_data.clear()
    st.rerun()

# កូដបង្កើត Item/Cart ក្នុង session
if "cart" not in st.session_state:
    st.session_state.cart = []

if "applied_discount_code" not in st.session_state:
    st.session_state.applied_discount_code = None
    st.session_state.applied_discount_pct = 0
    st.session_state.customer_name = ""

# បញ្ជីសេវាកម្ម/ទំនិញគំរូ
SERVICES_CATALOG = {
    "កាត់សក់ & កក់សក់": 5.00,
    "លាបពណ៌សក់": 15.00,
    "អ៊ុតត្រង់ / អ៊ុតរលក": 25.00,
    "កក់សក់បុរាណ / ម៉Massage": 8.00,
    "ធ្វើក្រចក (Manicure/Pedicure)": 10.00,
    "ស្ប៉ាមុខ / ថែរក្សាស្បែក": 20.00,
    "ប្រេងបំប៉នសក់ (ទំនិញ)": 12.00,
    "ឡេការពារកម្ដៅថ្ងៃ (ទំនិញ)": 18.00,
}

menu_option = st.sidebar.radio("👉 ជ្រើសរើសមេនូ៖", ["🛒 ប្រព័ន្ធគិតលុយ (POS)", "➕ បង្កើតកូដអតិថិជនថ្មី", "📊 តារាងតាមដានទិន្នន័យ"])

# ================================================================
# 🛒 មេនូទី ១៖ ប្រព័ន្ធគិតលុយ (POS System)
# ================================================================
if menu_option == "🛒 ប្រព័ន្ធគិតលុយ (POS)":
    st.title("🛒 ប្រព័ន្ធគិតលុយ & ចេញវិក្កយបត្រ (POS)")
    
    col_catalog, col_cart = st.columns([1.2, 1], gap="medium")
    
    # ------------------------------------------------------------
    # ផ្នែកខាងឆ្វេង៖ ជ្រើសរើសសេវាកម្ម / ទំនិញ
    # ------------------------------------------------------------
    with col_catalog:
        st.subheader("🛍️ ជ្រើសរើសសេវាកម្ម / ទំនិញ")
        
        # បង្កើត Grid សម្រាប់សេវាកម្ម
        cat_cols = st.columns(2)
        for i, (service_name, price) in enumerate(SERVICES_CATALOG.items()):
            with cat_cols[i % 2]:
                with st.container(border=True):
                    st.write(f"**{service_name}**")
                    st.write(f"💵 ${price:.2f} ({price * EXCHANGE_RATE:,.0f} ៛)")
                    if st.button(f"➕ បន្ថែម", key=f"add_{i}", use_container_width=True):
                        # បន្ថែមចូល Cart
                        found = False
                        for item in st.session_state.cart:
                            if item["name"] == service_name:
                                item["qty"] += 1
                                item["total"] = item["qty"] * item["price"]
                                found = True
                                break
                        if not found:
                            st.session_state.cart.append({
                                "name": service_name,
                                "price": price,
                                "qty": 1,
                                "total": price
                            })
                        st.rerun()

        # បញ្ចូលសេវាកម្មផ្ទាល់ខ្លួន (Custom Item)
        st.markdown("---")
        st.subheader("✍️ បញ្ចូលតម្លៃផ្សេងៗ / សេវាកម្មក្រៅបញ្ជី")
        c_col1, c_col2, c_col3 = st.columns([2, 1, 1])
        custom_name = c_col1.text_input("ឈ្មោះសេវា/ទំនិញ", key="custom_name")
        custom_price = c_col2.number_input("តម្លៃ ($)", min_value=0.0, step=0.5, key="custom_price")
        if c_col3.button("បន្ថែមទំនិញ", type="primary", use_container_width=True):
            if custom_name and custom_price > 0:
                st.session_state.cart.append({
                    "name": custom_name,
                    "price": custom_price,
                    "qty": 1,
                    "total": custom_price
                })
                st.rerun()

    # ------------------------------------------------------------
    # ផ្នែកខាងស្តាំ៖ បញ្ជីទំនិញក្នុង Cart & គណនាប្រាក់
    # ------------------------------------------------------------
    with col_cart:
        st.subheader("📋 បញ្ជីទិញទំនិញ (Cart)")
        
        if not st.session_state.cart:
            st.info("📭 មិនទាន់មានទំនិញក្នុងកញ្ចប់នៅឡើយទេ។")
        else:
            # បង្ហាញតារាង Cart
            cart_df = pd.DataFrame(st.session_state.cart)
            cart_df.columns = ["សេវាកម្ម", "តម្លៃ ($)", "បរិមាណ", "សរុប ($)"]
            st.dataframe(cart_df[["សេវាកម្ម", "តម្លៃ ($)", "បរិមាណ", "សរុប ($)"]], use_container_width=True, hide_index=True)
            
            if st.button("🗑️ សម្អាតកញ្ចប់ទំនិញ (Clear Cart)"):
                st.session_state.cart = []
                st.session_state.applied_discount_code = None
                st.session_state.applied_discount_pct = 0
                st.session_state.customer_name = ""
                st.rerun()

        st.markdown("---")
        st.subheader("🎟️ បញ្ចូលកូដណែនាំ (Referral Discount)")
        
        ref_code_input = st.text_input("🔍 វាយបញ្ចូលកូដកាតអតិថិជន (ឧទាហរណ៍៖ 10231010):").strip().upper()
        if st.button("ផ្ទៀងផ្ទាត់កូដ"):
            if ref_code_input and not df.empty:
                valid_rows = df[df["កូដកាត"] == ref_code_input]
                if not valid_rows.empty:
                    idx = valid_rows.index[-1]
                    owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                    try:
                        pts = int(float(df.loc[idx, "ចំនំនួនអ្នកណែនាំ"]))
                    except:
                        pts = 0
                    
                    pct = pts * 10 if pts < 10 else 100
                    st.session_state.applied_discount_code = ref_code_input
                    st.session_state.applied_discount_pct = pct
                    st.session_state.customer_name = owner_name
                    st.success(f"✅ កូដរបស់ **{owner_name}** ទទួលបានការបញ្ចុះតម្លៃ **{pct}%** ({pts} នាក់)!")
                else:
                    st.error("❌ មិនមានលេខកូដនេះក្នុងប្រព័ន្ធទេ!")
            else:
                st.warning("⚠️ សូមបញ្ចូលលេខកូដ!")

        # ------------------------------------------------------------
        # 📊 ការគណនាប្រាក់សរុប (Total Calculation)
        # ------------------------------------------------------------
        subtotal_usd = sum(item["total"] for item in st.session_state.cart)
        discount_pct = st.session_state.applied_discount_pct
        discount_usd = (subtotal_usd * discount_pct) / 100
        total_usd = subtotal_usd - discount_usd
        total_khr = round(total_usd * EXCHANGE_RATE)

        st.markdown("---")
        st.markdown("### 💰 សរុបទឹកប្រាក់ត្រូវបង់")
        st.write(f"តម្លៃដើមសរុប (Subtotal): **${subtotal_usd:.2f}**")
        if discount_pct > 0:
            st.write(f"បញ្ចុះតម្លៃ ({discount_pct}%): <span style='color:red;'>-${discount_usd:.2f}</span>", unsafe_allow_html=True)
        
        st.markdown(f"### <span style='color:green;'>សរុបចុងក្រោយ៖ ${total_usd:.2f} / {total_khr:,.0f} ៛</span>", unsafe_allow_html=True)

        # ------------------------------------------------------------
        # 💵 ការទទួលប្រាក់ និង គណនាប្រាក់អាប់
        # ------------------------------------------------------------
        st.markdown("---")
        st.subheader("💵 ការទូទាត់ប្រាក់")
        pay_col1, pay_col2 = st.columns(2)
        paid_usd = pay_col1.number_input("ប្រាក់ទទួលបាន ($)", min_value=0.0, step=1.0)
        paid_khr = pay_col2.number_input("ប្រាក់ទទួលបាន (៛)", min_value=0, step=1000)

        total_paid_usd = paid_usd + (paid_khr / EXCHANGE_RATE)
        change_usd = total_paid_usd - total_usd
        change_khr = round(change_usd * EXCHANGE_RATE)

        if total_paid_usd >= total_usd and total_usd > 0:
            st.success(f"💵 ប្រាក់អាប់៖ **${change_usd:.2f}** ({change_khr:,.0f} ៛)")
        elif total_paid_usd < total_usd and total_paid_usd > 0:
            st.warning(f"⚠️ ប្រាក់នៅខ្វះ៖ **${abs(change_usd):.2f}** ({abs(change_khr):,.0f} ៛)")

        # ------------------------------------------------------------
        # 🏁 ប៊ូតុងបញ្ចប់ការទូទាត់ និងបោះពុម្ពវិក្កយបត្រ
        # ------------------------------------------------------------
        if st.button("✅ បញ្ចប់ការទូទាត់ & ចេញវិក្កយបត្រ", type="primary", use_container_width=True):
            if not st.session_state.cart:
                st.error("❌ មិនទាន់មានទំនិញក្នុងកញ្ចប់ទិញនៅឡើយ!")
            elif total_paid_usd < total_usd:
                st.error("❌ ប្រាក់ទូទាត់មិនទាន់គ្រប់គ្រាន់ទេ!")
            else:
                # ប្រសិនបើមានប្រើ Discount Code ត្រូវ reset ពិន្ទុ ឬ បូកពិន្ទុបន្ថែម
                if st.session_state.applied_discount_code:
                    code = st.session_state.applied_discount_code
                    owner = st.session_state.customer_name
                    # បន្ទាប់ពីប្រើការបញ្ចុះតម្លៃរួច Reset ពិន្ទុមក 0 វិញ
                    params = {
                        "action": "update",
                        "code": code,
                        "name": owner,
                        "count": 0,
                        "status": "សកម្ម",
                        "image": ""
                    }
                    try:
                        requests.post(SCRIPT_URL, json=params)
                        st.cache_data.clear()
                    except:
                        pass

                st.balloons()
                st.success("🎉 ការទូទាត់ជោគជ័យ!")
                
                # បង្កើតវិក្កយបត្រ HTML សម្រាប់បោះពុម្ព
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                receipt_items_html = ""
                for item in st.session_state.cart:
                    receipt_items_html += f"""
                    <tr>
                        <td style='padding:4px;'>{item['name']}</td>
                        <td style='text-align:center;'>{item['qty']}</td>
                        <td style='text-align:right;'>${item['price']:.2f}</td>
                        <td style='text-align:right;'>${item['total']:.2f}</td>
                    </tr>
                    """

                receipt_html = f"""
                <div id="receipt" style="font-family: Arial, sans-serif; width: 300px; padding: 15px; border: 1px solid #ccc; background: #fff; color: #000; margin: auto;">
                    <h3 style="text-align:center; margin:0;">អូនឡែន សម្រស់</h3>
                    <p style="text-align:center; font-size:12px; margin:2px;">ទូរស័ព្ទ៖ 012 345 678 / 098 765 432</p>
                    <p style="text-align:center; font-size:11px; margin:2px;">កាលបរិច្ឆេទ៖ {now_str}</p>
                    <p style="text-align:center; font-size:11px; margin:2px;">អ្នកគិតលុយ៖ {st.session_state.username}</p>
                    <hr style="border-top: 1px dashed #000;">
                    <table style="width:100%; font-size:12px; border-collapse:collapse;">
                        <thead>
                            <tr style="border-bottom: 1px solid #000;">
                                <th style="text-align:left;">មុខទំនិញ</th>
                                <th style="text-align:center;">ចំនួន</th>
                                <th style="text-align:right;">តម្លៃ</th>
                                <th style="text-align:right;">សរុប</th>
                            </tr>
                        </thead>
                        <tbody>
                            {receipt_items_html}
                        </tbody>
                    </table>
                    <hr style="border-top: 1px dashed #000;">
                    <table style="width:100%; font-size:12px;">
                        <tr><td>សរុបដើម៖</td><td style="text-align:right;">${subtotal_usd:.2f}</td></tr>
                        <tr><td>បញ្ចុះតម្លៃ ({discount_pct}%):</td><td style="text-align:right;">-${discount_usd:.2f}</td></tr>
                        <tr style="font-weight:bold;"><td>ត្រូវបង់សរុប៖</td><td style="text-align:right;">${total_usd:.2f}</td></tr>
                        <tr style="font-weight:bold;"><td>ត្រូវបង់ជាប្រាក់រៀល៖</td><td style="text-align:right;">{total_khr:,.0f} ៛</td></tr>
                        <tr><td>ប្រាក់ទទួលបាន៖</td><td style="text-align:right;">${total_paid_usd:.2f}</td></tr>
                        <tr><td>ប្រាក់អាប់៖</td><td style="text-align:right;">${change_usd:.2f} ({change_khr:,.0f} ៛)</td></tr>
                    </table>
                    <hr style="border-top: 1px dashed #000;">
                    <p style="text-align:center; font-size:11px;">សូមអរគុណ ៖ សូមអញ្ជើញមកសារជាថ្មី! 🙏</p>
                </div>
                """
                
                st.markdown("### 🧾 វិក្កយបត្រទូទាត់ប្រាក់")
                st.components.v1.html(receipt_html, height=450, scrolling=True)

                # Reset Cart ក្រោយពេលគិតលុយរួច
                st.session_state.cart = []
                st.session_state.applied_discount_code = None
                st.session_state.applied_discount_pct = 0
                st.session_state.customer_name = ""

# ================================================================
# ➕ មេនូទី ២៖ បង្កើតកូដអតិថិជនថ្មី
# ================================================================
elif menu_option == "➕ បង្កើតកូដអតិថិជនថ្មី":
    st.title("➕ បង្កើតកូដអតិថិជនថ្មី")
    col1, col2 = st.columns(2)
    with col1:
        new_code = st.text_input("លេខកូដថ្មី (ឧទាហរណ៍៖ 10231010):").strip().upper()
    with col2:
        new_name = st.text_input("ឈ្មោះអតិថិជន:")

    if st.button("ចុះឈ្មោះកូដថ្មី", type="primary", use_container_width=True):
        if new_code and new_name:
            if not df.empty and new_code in df["កូដកាត"].values:
                st.error("❌ លេខកូដនេះមានរួចហើយ!")
            else:
                params = {
                    "action": "create",
                    "code": new_code,
                    "name": new_name,
                    "image": ""
                }
                response = requests.post(SCRIPT_URL, json=params)
                if response.status_code == 200:
                    st.cache_data.clear()
                    st.success(f"🎉 បង្កើតកូដ {new_code} ជូនលោក/លោកស្រី {new_name} ជោគជ័យ!")
                else:
                    st.error("❌ មិនអាចចុះឈ្មោះបានទេ!")
        else:
            st.warning("⚠️ សូមបំពេញព័ត៌មានឱ្យបានគ្រប់គ្រាន់។")

# ================================================================
# 📊 មេនូទី ៣៖ តារាងតាមដានទិន្នន័យ
# ================================================================
else:
    st.title("📊 តារាងតាមដានទិន្នន័យអតិថិជន & កូដណែនាំ")
    if not df.empty:
        display_df = df.drop_duplicates(subset=["កូដកាត"], keep="last").copy()
        
        def calculate_discount(x):
            try:
                val = int(float(x))
                return f"{val * 10}%" if val < 10 else "FREE 1 ដង"
            except:
                return "0%"
                
        display_df["ភាគរយបញ្ចុះតម្លៃសន្សំបាន"] = display_df["ចំនំនួនអ្នកណែនាំ"].apply(calculate_discount)
        final_cols = ["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព", "ភាគរយបញ្ចុះតម្លៃសន្សំបាន"]
        
        st.dataframe(display_df[final_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.info("📭 មិនទាន់មានទិន្នន័យនៅក្នុងប្រព័ន្ធឡើយ។")
