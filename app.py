import streamlit as st
import pandas as pd
import requests
import hashlib
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration & Custom POS Styling
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Professional POS System",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom POS Styling ពណ៌បៃតង តាមទម្រង់ POS Real-time
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .customer-info-box {
        background-color: #0d8a43;
        color: white;
        padding: 12px 15px;
        border-radius: 6px 6px 0px 0px;
        font-size: 14px;
        line-height: 1.6;
    }
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
    .pos-footer-bar {
        background-color: #0d8a43;
        color: white;
        padding: 8px 15px;
        border-radius: 4px;
        font-size: 12px;
        margin-top: 15px;
    }
    .stButton>button {
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# អត្រាប្ដូរប្រាក់
EXCHANGE_RATE = 4100

# ----------------------------------------------------------------
# 2. បញ្ជីសេវាកម្មទាំងអស់ដែលបានដកស្រង់ចេញពីរូបភាព (SERVICES CATALOG)
# ----------------------------------------------------------------
SERVICES_CATALOG = [
    # --- សេវាកម្ម (General Services) ---
    {"code": "S01", "category": "សេវាកម្ម", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ", "price": 15.0},
    {"code": "S02", "category": "សេវាកម្ម", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីន baby Glow", "price": 15.0},
    {"code": "S03", "category": "សេវាកម្ម", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីន college", "price": 12.5},
    {"code": "S04", "category": "សេវាកម្ម", "name": "ញេចសម្អាតគ្រាប់មុន ជម្រុះកោសិកា", "price": 7.5},
    {"code": "S05", "category": "សេវាកម្ម", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនVIP ពីមុខ ដល់ ក", "price": 25.0},
    {"code": "S06", "category": "សេវាកម្ម", "name": "កក់សក់ + បិទម៉ាស", "price": 4.0},
    {"code": "S07", "category": "សេវាកម្ម", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនក្លៀកសរ ថែមបាញ់ laser ក្លៀក", "price": 15.0},
    {"code": "S08", "category": "សេវាកម្ម", "name": "ញេចសម្អាតមុនខ្នងជម្រុះកោសិកា", "price": 12.5},
    {"code": "S09", "category": "សេវាកម្ម", "name": "ញេចសម្អាតមុនខ្នង + ម៉ាសស្កាតបញ្ចូលវីតាមីន", "price": 20.0},

    # --- សេវាកម្ម Laser ---
    {"code": "L01", "category": "សេវាកម្ម Laser", "name": "បាញ់ Laser ក្លៀក", "price": 5.0},
    {"code": "L02", "category": "សេវាកម្ម Laser", "name": "បាញ់ Laser រោមដៃ", "price": 9.0},
    {"code": "L03", "category": "សេវាកម្ម Laser", "name": "បាញ់ Laser រោមជើង", "price": 9.0},
    {"code": "L04", "category": "សេវាកម្ម Laser", "name": "បាញ់ Bikini", "price": 12.0},
    {"code": "L05", "category": "សេវាកម្ម Laser", "name": "បករោម ក្លៀក", "price": 3.0},
    {"code": "L06", "category": "សេវាកម្ម Laser", "name": "បករោម ពុកមាត់", "price": 3.0},

    # --- សេវាកម្ម ស្ប៉ា ---
    {"code": "P01", "category": "សេវាកម្ម ស្ប៉ា", "name": "ឈុតស្ប៉ាស្បែក", "price": 10.0},
    {"code": "P02", "category": "សេវាកម្ម ស្ប៉ា", "name": "ឈុតស្ប៉ាដោះគោស្រស់", "price": 15.0},
    {"code": "P03", "category": "សេវាកម្ម ស្ប៉ា", "name": "ឈុតស្ប៉ាដោះគោស្រស់កូនក្រមុំ", "price": 20.0},
    
    # --- កញ្ចប់ប្រូម៉ូសិន (Special Package) ---
    {"code": "PKG", "category": "កញ្ចប់ពិសេស", "name": "កញ្ចប់ព្យាបាលមុន (3 ថែម 1 និង 5 ថែម 2)", "price": 0.0}
]

# ----------------------------------------------------------------
# 3. Google Sheets Connection & Session Setup
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

# Session State Setup
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

# ----------------------------------------------------------------
# 4. Main POS Layout (2 Columns: Left = Products/Cart, Right = Checkout)
# ----------------------------------------------------------------
col_left, col_right = st.columns([3.2, 1.2], gap="small")

# ================================================================
# LEFT PANEL: Search/Scan & Service Catalog Tabs
# ================================================================
with col_left:
    # Header Top Bar
    top_c1, top_c2, top_c3 = st.columns([1, 4, 1.5])
    with top_c1:
        st.checkbox("Show all UoM", value=False)
    with top_c2:
        search_query = st.text_input("Scan Barcode...", placeholder="[|||] Scan / វាយបញ្ចូលកូដ ឬ ឈ្មោះសេវាកម្ម...", label_visibility="collapsed")
    with top_c3:
        st.radio("Search Mode", ["Search", "Barcode"], index=1, horizontal=True, label_visibility="collapsed")

    # ការបន្ថែមតាមរយៈ Search / Barcode Scan
    if search_query:
        matched = next((item for item in SERVICES_CATALOG if item["code"].lower() == search_query.strip().lower() or search_query.strip().lower() in item["name"].lower()), None)
        if matched:
            existing = next((i for i in st.session_state.cart if i["code"] == matched["code"]), None)
            if existing:
                existing["qty"] += 1
                existing["total"] = existing["qty"] * existing["price"]
            else:
                st.session_state.cart.append({
                    "code": matched["code"],
                    "name": matched["name"],
                    "price": matched["price"],
                    "qty": 1,
                    "total": matched["price"]
                })
            st.rerun()

    # បែងចែកសេវាកម្មជា Tabs តាមប្រភេទ
    tab_gen, tab_laser, tab_spa = st.tabs(["✨ សេវាកម្មទូទៅ", "⚡ សេវាកម្ម Laser", "🧴 សេវាកម្ម ស្ប៉ា"])

    def render_catalog_category(category_name):
        items = [i for i in SERVICES_CATALOG if i["category"] == category_name]
        cols = st.columns(3)
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                btn_label = f"{item['name']}\n${item['price']:.2f} [{item['code']}]"
                if st.button(btn_label, key=f"cat_{item['code']}", use_container_width=True):
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

    with tab_gen:
        render_catalog_category("សេវាកម្ម")
    with tab_laser:
        render_catalog_category("សេវាកម្ម Laser")
    with tab_spa:
        render_catalog_category("សេវាកម្ម ស្ប៉ា")

    st.markdown("---")
    
    # Cart Data Table Area
    st.markdown("##### 📋 បញ្ជីសេវាកម្មដែលបានជ្រើសរើស (Cart Table)")
    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        cart_df.columns = ["កូដ", "ឈ្មោះសេវាកម្ម", "តម្លៃ ($)", "បរិមាណ", "សរុប ($)"]
        st.dataframe(cart_df[["កូដ", "ឈ្មោះសេវាកម្ម", "តម្លៃ ($)", "បរិមាណ", "សរុប ($)"]], use_container_width=True, hide_index=True)
    else:
        st.info("💡 មិនទាន់មានសេវាកម្មក្នុង Cart នៅឡើយទេ! សូមជ្រើសរើសសេវាកម្មខាងលើ។")

# ================================================================
# RIGHT PANEL: Customer Info & Total Summary
# ================================================================
with col_right:
    # 1. Customer & Shift Box
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

    st.markdown("""
    <div class="total-summary-header">Total Summary</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="total-summary-body">
        <div class="summary-row"><span>Sub Total:</span> <span>$ {subtotal:.2f}</span></div>
        <div class="summary-row"><span>Discount ({st.session_state.discount_pct}%):</span> <span>$ {discount_val:.2f}</span></div>
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

    # 3. Action Buttons Grid
    btn_c1, btn_c2, btn_c3 = st.columns(3)
    with btn_c1:
        if st.button("💵\nPayment", key="btn_pay", use_container_width=True, type="primary"):
            st.session_state.show_payment_modal = True
    with btn_c2:
        if st.button("💾\nSave/Hold", key="btn_hold", use_container_width=True):
            if st.session_state.cart:
                st.session_state.hold_list.append(st.session_state.cart.copy())
                st.session_state.cart = []
                st.toast("រក្សាទុក Order រួចរាល់!")
                st.rerun()
    with btn_c3:
        if st.button("📋\nHold List", key="btn_hold_list", use_container_width=True):
            st.info(f"ចំនួន Order ដែល Hold: {len(st.session_state.hold_list)}")

    btn_c4, btn_c5, btn_c6 = st.columns(3)
    with btn_c4:
        if st.button("%\nDiscount", key="btn_discount", use_container_width=True):
            st.session_state.show_discount_dialog = True
    with btn_c5:
        if st.button("🔑\nCustomer", key="btn_customer", use_container_width=True):
            st.session_state.show_customer_dialog = True
    with btn_c6:
        if st.button("🔍\nCheck Price", key="btn_check_price", use_container_width=True):
            st.toast("ពិនិត្យតម្លៃ...")

    btn_c7, btn_c8, btn_c9 = st.columns(3)
    with btn_c7:
        if st.button("🖨️\nRe-Print", key="btn_reprint", use_container_width=True):
            st.toast("បោះពុម្ពវិក្កយបត្រឡើងវិញ...")
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
# Modals / Popups
# ----------------------------------------------------------------
if st.session_state.get("show_customer_dialog", False):
    with st.expander("🔑 ភ្ជាប់កូដអតិថិជន (Referral Discount)", expanded=True):
        c_code = st.text_input("បញ្ចូលកូដអតិថិជន:").strip().upper()
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
                    st.success(f"ភ្ជាប់កូដ {name} ជោគជ័យ! Discount {pct}%")
                    st.rerun()
                else:
                    st.error("មិនមានកូដនេះទេ!")
            else:
                st.session_state.show_customer_dialog = False
                st.rerun()

if st.session_state.get("show_payment_modal", False):
    with st.expander("💵 ការទូទាត់ប្រាក់ (Payment)", expanded=True):
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

# Bottom Shortcut Bar
st.markdown("""
<div class="pos-footer-bar">
    <span style="margin-right: 20px;"><b>Shift + F1</b> => Switch Filter Type</span>
    <span style="margin-right: 20px;"><b>Shift + F2</b> => Focus Filter Box</span>
    <span style="margin-right: 20px;"><b>Shift + F3</b> => Switch Show all UoM</span>
    <span style="float: right;"><b>Warehouse:</b> Main Store | <b>Outlet:</b> OunLen SMR</span>
</div>
""", unsafe_allow_html=True)
