import streamlit as st
import pandas as pd
import requests
import hashlib
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration & Custom POS Styling ( Green Theme )
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Professional POS System",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# កំណត់ CSS ឱ្យចេញស្ទាយ៍ទម្រង់ POS ដូចរូបថត
st.markdown("""
<style>
    /* background ផ្ទៃក្រោយ */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Customer Info Box Style ពណ៌បៃតង */
    .customer-info-box {
        background-color: #0d8a43;
        color: white;
        padding: 12px 15px;
        border-radius: 6px 6px 0px 0px;
        font-size: 14px;
        line-height: 1.6;
    }

    /* Total Summary Box */
    .total-summary-header {
        background-color: #0d8a43;
        color: white;
        padding: 10px 15px;
        font-weight: bold;
        font-size: 15px;
        border-radius: 6px 6px 0px 0px;
        margin-top: 10px;
    }

    .total-summary-body {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-top: none;
        padding: 12px 15px;
        font-size: 13px;
        color: #333;
        line-height: 1.8;
    }

    .summary-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }

    .grand-total-usd {
        color: #d9534f;
        font-size: 22px;
        font-weight: bold;
    }

    .grand-total-khr {
        color: #d9534f;
        font-size: 18px;
        font-weight: bold;
    }

    /* POS Status Bar ខាងក្រោម */
    .pos-footer-bar {
        background-color: #0d8a43;
        color: white;
        padding: 8px 15px;
        border-radius: 4px;
        font-size: 12px;
        margin-top: 15px;
    }
    
    /* កែសម្រួល Styling ប៊ូតុង */
    .stButton>button {
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# អត្រាប្ដូរប្រាក់
EXCHANGE_RATE = 4100

# ----------------------------------------------------------------
# 2. ទាញយកទិន្នន័យ Referral Code ពី Google Sheets
# ----------------------------------------------------------------
try:
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    SCRIPT_URL = st.secrets["connections"]["gsheets"]["script_url"]
    if "docs.google.com/spreadsheets" in spreadsheet_url:
        spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Referral"
    else:
        csv_url = spreadsheet_url
except Exception:
    SCRIPT_URL = ""
    csv_url = ""

@st.cache_data(ttl=5)
def load_data(url):
    if not url:
        return pd.DataFrame()
    try:
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame()

raw_df = load_data(csv_url)
df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព"])

if not raw_df.empty:
    raw_df.columns = [str(col).strip() for col in raw_df.columns]
    if len(raw_df.columns) >= 5:
        df["កូដកាត"] = raw_df.iloc[:, 1].astype(str).str.strip().str.upper()
        df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 2]
        df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 3]
        df["ស្ថានភាព"] = raw_df.iloc[:, 4]

# ----------------------------------------------------------------
# 3. Session State setup
# ----------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # កំណត់ True ដើម្បីងាយស្រួល Testing
    st.session_state.username = "Cashier 01"

if "cart" not in st.session_state:
    st.session_state.cart = []

if "customer_name" not in st.session_state:
    st.session_state.customer_name = "General"

if "customer_code" not in st.session_state:
    st.session_state.customer_code = "N/A"

if "discount_pct" not in st.session_state:
    st.session_state.discount_pct = 0.0

if "vat_pct" not in st.session_state:
    st.session_state.vat_pct = 0.0

if "service_charge" not in st.session_state:
    st.session_state.service_charge = 0.0

if "hold_list" not in st.session_state:
    st.session_state.hold_list = []

# បញ្ជីទំនិញ/សេវាកម្មគំរូ សម្រាប់ជ្រើសរើស ឬ Scan
SAMPLE_ITEMS = [
    {"code": "1001", "name": "កាត់សក់ & កក់សក់", "price": 5.00},
    {"code": "1002", "name": "លាបពណ៌សក់", "price": 15.00},
    {"code": "1003", "name": "អ៊ុតត្រង់ / អ៊ុតរលក", "price": 25.00},
    {"code": "1004", "name": "កក់សក់បុរាណ", "price": 8.00},
    {"code": "1005", "name": "ធ្វើក្រចក (Manicure)", "price": 10.00},
    {"code": "1006", "name": "ស្ប៉ាមុខ / ថែរក្សាស្បែក", "price": 20.00},
]

# ----------------------------------------------------------------
# 4. POS Interface Layout (ចែកជា ២ Column ធំៗដូចរូបថត)
# ----------------------------------------------------------------
col_left, col_right = st.columns([3.2, 1.2], gap="small")

# ================================================================
# ផ្នែកខាងឆ្វេង (LEFT PANEL): Header Scan Barcode, Catalog, Cart Table
# ================================================================
with col_left:
    # Top Filter / Barcode Scan Bar (ដូចផ្នែកខាងលើរូបថត)
    top_c1, top_c2, top_c3 = st.columns([1, 4, 1.5])
    
    with top_c1:
        st.checkbox("Show all UoM", value=False)
        
    with top_c2:
        search_query = st.text_input("Scan Barcode...", placeholder="[|||] Scan Barcode / វាយបញ្ចូលកូដទំនិញ...", label_visibility="collapsed")
        
    with top_c3:
        search_mode = st.radio("Search Mode", ["Search", "Barcode"], index=1, horizontal=True, label_visibility="collapsed")

    # បើមានការ Scan Barcode ឬ វាយបញ្ចូលកូដ
    if search_query:
        matched_item = next((item for item in SAMPLE_ITEMS if item["code"].lower() == search_query.strip().lower() or item["name"].lower() == search_query.strip().lower()), None)
        if matched_item:
            existing = next((i for i in st.session_state.cart if i["code"] == matched_item["code"]), None)
            if existing:
                existing["qty"] += 1
                existing["total"] = existing["qty"] * existing["price"]
            else:
                st.session_state.cart.append({
                    "code": matched_item["code"],
                    "name": matched_item["name"],
                    "price": matched_item["price"],
                    "qty": 1,
                    "total": matched_item["price"]
                })
            st.rerun()

    # Quick Select Items Catalog
    st.markdown("##### 📦 មុខទំនិញ / សេវាកម្ម (Quick Select Catalog)")
    catalog_cols = st.columns(3)
    for idx, item in enumerate(SAMPLE_ITEMS):
        with catalog_cols[idx % 3]:
            if st.button(f"🛒 {item['name']}\n${item['price']:.2f} [{item['code']}]", key=f"cat_{item['code']}", use_container_width=True):
                existing = next((i for i in st.session_state.cart if i["code"] == item["code"]), None)
                if existing:
                    existing["qty"] += 1
                    existing["total"] = existing["qty"] * existing["price"]
                else:
                    st.session_state.cart.append({
                        "code": item["code"],
                        "name": item["name"],
                        "price": item["price"],
                        "qty": 1,
                        "total": item["price"]
                    })
                st.rerun()

    st.markdown("---")
    
    # តារាង Cart Table បង្ហាញបញ្ជីទំនិញ
    st.markdown("##### 📋 បញ្ជីទំនិញដែលបានជ្រើសរើស (Cart Table)")
    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        cart_df.columns = ["កូដ", "ឈ្មោះសេវាកម្ម/ទំនិញ", "តម្លៃ ($)", "បរិមាណ", "សរុប ($)"]
        st.dataframe(cart_df[["កូដ", "ឈ្មោះសេវាកម្ម/ទំនិញ", "តម្លៃ ($)", "បរិមាណ", "សរុប ($)"]], use_container_width=True, hide_index=True)
    else:
        st.info("💡 មិនទាន់មានទំនិញក្នុង Cart នៅឡើយទេ! សូម Scan Barcode ឬ ចុចលើ Catalog ខាងលើ។")

# ================================================================
# ផ្នែកខាងស្តាំ (RIGHT PANEL): Customer, Shift, Total Summary, Action Buttons
# ================================================================
with col_right:
    # 1. Customer & Shift Info Box (ពណ៌បៃតងខាងលើស្តាំ)
    st.markdown(f"""
    <div class="customer-info-box">
        <div>👤 <b>Customer:</b> {st.session_state.customer_name}</div>
        <div>💳 <b>Customer No.:</b> {st.session_state.customer_code}</div>
        <hr style="margin: 8px 0; border-color: rgba(255,255,255,0.3);">
        <div># <b>Shift No.:</b> #001</div>
        <div>🕒 <b>Shift Start:</b> {datetime.now().strftime('%H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Total Summary Calculations
    subtotal = sum(item["total"] for item in st.session_state.cart)
    discount_val = (subtotal * st.session_state.discount_pct) / 100
    after_discount = subtotal - discount_val
    vat_val = (after_discount * st.session_state.vat_pct) / 100
    service_charge_val = st.session_state.service_charge
    grand_total_usd = after_discount + vat_val + service_charge_val
    grand_total_khr = round(grand_total_usd * EXCHANGE_RATE)

    # Total Summary Display Box (ដូចរូប)
    st.markdown("""
    <div class="total-summary-header">
        Total Summary
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="total-summary-body">
        <div class="summary-row"><span>Sub Total:</span> <span>$ {subtotal:.2f}</span></div>
        <div class="summary-row"><span>Discount:</span> <span>$ {discount_val:.2f}</span></div>
        <div class="summary-row"><span>VAT:</span> <span>$ {vat_val:.2f}</span></div>
        <div class="summary-row"><span>S/Charge:</span> <span>$ {service_charge_val:.2f}</span></div>
        <hr style="margin: 6px 0; border-top: 1px dashed #ccc;">
        <div class="summary-row" style="align-items: baseline;">
            <span style="font-weight:bold;">Grand Total:</span> 
            <span class="grand-total-usd">$ {grand_total_usd:.2f}</span>
        </div>
        <div class="summary-row" style="justify-content: flex-end;">
            <span class="grand-total-khr">៛ {grand_total_khr:,.0f}</span>
        </div>
        <hr style="margin: 6px 0; border-top: 1px dashed #ccc;">
        <div class="summary-row" style="font-size: 11px; color: #666;">
            <span>Rate:</span> <span>1 USD = {EXCHANGE_RATE} KHR</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # 3. Action Control Grid Buttons (ប៊ូតុងខាងក្រោមស្តាំ)
    btn_c1, btn_c2, btn_c3 = st.columns(3)
    with btn_c1:
        if st.button("💵\nPayment", key="btn_pay", use_container_width=True, type="primary"):
            st.session_state.show_payment_modal = True

    with btn_c2:
        if st.button("💾\nSave / Hold", key="btn_hold", use_container_width=True):
            if st.session_state.cart:
                st.session_state.hold_list.append(st.session_state.cart.copy())
                st.session_state.cart = []
                st.toast("រក្សាទុកកញ្ចប់ទំនិញរួចរាល់! (Hold Saved)")
                st.rerun()

    with btn_c3:
        if st.button("📋\nHold List", key="btn_hold_list", use_container_width=True):
            st.info(f"ចំនួន Order ដែលបាន Hold: {len(st.session_state.hold_list)}")

    btn_c4, btn_c5, btn_c6 = st.columns(3)
    with btn_c4:
        if st.button("%\nDiscount", key="btn_discount", use_container_width=True):
            st.session_state.show_discount_dialog = True

    with btn_c5:
        if st.button("🔑\nCustomer", key="btn_customer", use_container_width=True):
            st.session_state.show_customer_dialog = True

    with btn_c6:
        if st.button("🔍\nCheck Price", key="btn_check_price", use_container_width=True):
            st.toast("មុខងារពិនិត្យតម្លៃ...")

    btn_c7, btn_c8, btn_c9 = st.columns(3)
    with btn_c7:
        if st.button("🖨️\nRe-Print", key="btn_reprint", use_container_width=True):
            st.toast("កំពុងបោះពុម្ពវិក្កយបត្រឡើងវិញ...")

    with btn_c8:
        if st.button("🗑️\nClear Cart", key="btn_clear", use_container_width=True):
            st.session_state.cart = []
            st.session_state.discount_pct = 0.0
            st.session_state.customer_name = "General"
            st.session_state.customer_code = "N/A"
            st.rerun()

    with btn_c9:
        if st.button("⚙️\nMore", key="btn_more", use_container_width=True):
            st.toast("មុខងារបន្ថែម...")

# ----------------------------------------------------------------
# Dialogs & Modal Popups
# ----------------------------------------------------------------
# Customer Search Modal
if st.session_state.get("show_customer_dialog", False):
    with st.expander("🔑 ភ្ជាប់កូដអតិថិជន (Customer Referral Code)", expanded=True):
        c_code = st.text_input("បញ្ចូលកូដអតិថិជន ( Referral Code ):").strip().upper()
        if st.button("ស្វែងរក និង ភ្ជាប់កូដ"):
            if c_code and not df.empty:
                v_rows = df[df["កូដកាត"] == c_code]
                if not v_rows.empty:
                    idx = v_rows.index[-1]
                    name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                    try:
                        pts = int(float(df.loc[idx, "ចំនំនួនអ្នកណែនាំ"]))
                    except:
                        pts = 0
                    pct = pts * 10 if pts < 10 else 100
                    st.session_state.customer_name = name
                    st.session_state.customer_code = c_code
                    st.session_state.discount_pct = float(pct)
                    st.session_state.show_customer_dialog = False
                    st.success(f"ភ្ជាប់កូដជោគជ័យ! ទទួលបាន Discount {pct}%")
                    st.rerun()
                else:
                    st.error("មិនមានកូដនេះក្នុងប្រព័ន្ធទេ!")
            else:
                st.session_state.customer_name = "General"
                st.session_state.customer_code = c_code if c_code else "N/A"
                st.session_state.show_customer_dialog = False
                st.rerun()

# Payment Checkout Modal
if st.session_state.get("show_payment_modal", False):
    with st.expander("💵 ការទូទាត់ប្រាក់ (Payment Modal)", expanded=True):
        st.write(f"### ត្រូវបង់សរុប៖ **$ {grand_total_usd:.2f}** ({grand_total_khr:,.0f} ៛)")
        p_col1, p_col2 = st.columns(2)
        paid_usd = p_col1.number_input("ប្រាក់ទទួលបាន ($)", min_value=0.0, value=grand_total_usd)
        paid_khr = p_col2.number_input("ប្រាក់ទទួលបាន (៛)", min_value=0, step=1000)
        
        tot_paid = paid_usd + (paid_khr / EXCHANGE_RATE)
        change_u = tot_paid - grand_total_usd
        change_k = round(change_u * EXCHANGE_RATE)
        
        st.info(f"💵 ប្រាក់អាប់៖ $ {change_u:.2f} ({change_k:,.0f} ៛)")
        
        if st.button("Confirm Payment & Reset Cart", type="primary"):
            st.balloons()
            st.session_state.cart = []
            st.session_state.show_payment_modal = False
            st.session_state.discount_pct = 0.0
            st.session_state.customer_name = "General"
            st.session_state.customer_code = "N/A"
            st.success("🎉 ទូទាត់ប្រាក់ជោគជ័យ!")
            st.rerun()

# ----------------------------------------------------------------
# 5. Bottom Shortcut Status Bar (បាតខាងក្រោមដូចរូបថត)
# ----------------------------------------------------------------
st.markdown("""
<div class="pos-footer-bar">
    <span style="margin-right: 20px;"><b>Shift + F1</b> => Switch Filter Type</span>
    <span style="margin-right: 20px;"><b>Shift + F2</b> => Focus Filter Box</span>
    <span style="margin-right: 20px;"><b>Shift + F3</b> => Switch Show all UoM</span>
    <span style="float: right;"><b>Warehouse:</b> Main Store | <b>Outlet:</b> OunLen SMR</span>
</div>
""", unsafe_allow_html=True)
