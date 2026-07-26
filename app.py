import streamlit as st
import pandas as pd
import json
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Professional POS & Sales Report",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for UI Enhancement (ប្តូរទៅជាពណ៌ផ្កាឈូកស្រាល - Light Pink Theme)
st.markdown("""
<style>
    /* 1. Background App ទាំងមូល (ប្តូរទៅជាពណ៌ផ្កាឈូកស្រាល) */
    .stApp {
        background-color: #fdf2f8 !important; /* Soft Light Pink */
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif;
        color: #0f172a;
    }
    
    /* 2. Navigation Menu ខាងលើ */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    div[data-testid="stRadio"] > div {
        background-color: #1e293b !important;
        padding: 8px 16px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] span {
        color: #ffffff !important; /* អក្សរពណ៌សច្បាស់ */
        font-size: 15px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] input:checked + div {
        background-color: #db2777 !important; /* ពណ៌ផ្កាឈូកចាស់ពេល Hover/Select */
    }

    /* 3. Tabs (សេវាកម្មទូទៅ / Laser / ស្ប៉ា) */
    button[data-baseweb="tab"] p {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    button[aria-selected="true"] p {
        color: #db2777 !important; /* ពណ៌ផ្កាឈូកពេលជ្រើសរើស Tab */
        font-weight: bold !important;
    }

    /* 4. Circle Button Styling (ប៊ូតុងរង្វង់សេវាកម្ម) */
    div.stButton > button {
        border-radius: 50% !important;
        width: 125px !important;
        height: 125px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #ffffff !important;
        text-shadow: 0px 1px 3px rgba(0, 0, 0, 0.8) !important;
        border: 3px solid #ffffff !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
        transition: all 0.2s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: auto !important;
        padding: 10px !important;
        text-align: center !important;
    }
    
    div.stButton > button:hover {
        transform: scale(1.08) !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.25) !important;
        border-color: #f59e0b !important;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    }

    /* 5. POS Action Buttons (ប៊ូតុងមុខងារខាងស្តាំ) */
    .pos-btn div.stButton > button {
        border-radius: 8px !important;
        width: 100% !important;
        height: 48px !important;
        background: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-shadow: none !important;
    }
    
    .pos-btn div.stButton > button:hover {
        background: #1e293b !important;
        border-color: #ec4899 !important;
    }
    
    .pay-btn div.stButton > button {
        border-radius: 8px !important;
        width: 100% !important;
        height: 52px !important;
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-shadow: none !important;
    }

    /* 6. Customer Info Box */
    .customer-info-box {
        background-color: #047857;
        color: #ffffff;
        padding: 14px 16px;
        border-radius: 8px 8px 0px 0px;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* 7. Total Summary Box */
    .total-summary-header {
        background-color: #047857;
        color: #ffffff;
        padding: 10px 15px;
        font-weight: bold;
        font-size: 15px;
        border-radius: 8px 8px 0px 0px;
        margin-top: 10px;
    }
    
    .total-summary-body {
        background-color: #ffffff;
        border: 1px solid #fbcfe8;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 15px;
        font-size: 13px;
        color: #0f172a;
        line-height: 1.8;
    }

    .summary-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }
    
    .grand-total-usd {
        color: #dc2626;
        font-size: 24px;
        font-weight: bold;
    }
    
    .grand-total-khr {
        color: #dc2626;
        font-size: 18px;
        font-weight: bold;
    }

    /* 8. Receipt Box Styling */
    .receipt-container {
        background: #fff5f7;
        border: 2px dashed #ec4899;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        color: #0f172a;
    }

    /* 9. Metric Cards Styling */
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #db2777;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .pos-footer-bar {
        background-color: #0f172a;
        color: #ffffff;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 12px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. Data Initialization & Setup
# ----------------------------------------------------------------
EXCHANGE_RATE = 4100

SERVICES_CATALOG = [
    # --- សេវាកម្ម (General Services) ---
    {"code": "S01", "category": "សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ", "price": 15.0, "icon": "🌿"},
    {"code": "S02", "category": "សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីន baby Glow", "price": 15.0, "icon": "✨"},
    {"code": "S03", "category": "សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីន college", "price": 12.5, "icon": "💧"},
    {"code": "S04", "category": "សេវាកម្មទូទៅ", "name": "ញេចសម្អាតគ្រាប់មុន ជម្រុះកោសិកា", "price": 7.5, "icon": "🧖‍♀️"},
    {"code": "S05", "category": "សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនVIP ពីមុខ ដល់ ក", "price": 25.0, "icon": "👑"},
    {"code": "S06", "category": "សេវាកម្មទូទៅ", "name": "កក់សក់ + បិទម៉ាស", "price": 4.0, "icon": "💇‍♀️"},
    {"code": "S07", "category": "សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនក្លៀកសរ ថែមបាញ់ laser ក្លៀក", "price": 15.0, "icon": "🌸"},
    {"code": "S08", "category": "សេវាកម្មទូទៅ", "name": "ញេចសម្អាតមុនខ្នងជម្រុះកោសិកា", "price": 12.5, "icon": "🛁"},
    {"code": "S09", "category": "សេវាកម្មទូទៅ", "name": "ញេចសម្អាតមុនខ្នង + ម៉ាសស្កាតបញ្ចូលវីតាមីន", "price": 20.0, "icon": "🌺"},

    # --- សេវាកម្ម Laser ---
    {"code": "L01", "category": "សេវាកម្ម Laser", "name": "បាញ់ Laser ក្លៀក", "price": 5.0, "icon": "⚡"},
    {"code": "L02", "category": "សេវាកម្ម Laser", "name": "បាញ់ Laser រោមដៃ", "price": 9.0, "icon": "⚡"},
    {"code": "L03", "category": "សេវាកម្ម Laser", "name": "បាញ់ Laser រោមជើង", "price": 9.0, "icon": "⚡"},
    {"code": "L04", "category": "សេវាកម្ម Laser", "name": "បាញ់ Bikini", "price": 12.0, "icon": "👙"},
    {"code": "L05", "category": "សេវាកម្ម Laser", "name": "បករោម ក្លៀក", "price": 3.0, "icon": "✨"},
    {"code": "L06", "category": "សេវាកម្ម Laser", "name": "បករោម ពុកមាត់", "price": 3.0, "icon": "✂️"},

    # --- សេវាកម្ម ស្ប៉ា ---
    {"code": "P01", "category": "សេវាកម្ម ស្ប៉ា", "name": "ឈុតស្ប៉ាស្បែក", "price": 10.0, "icon": "🧴"},
    {"code": "P02", "category": "សេវាកម្ម ស្ប៉ា", "name": "ឈុតស្ប៉ាដោះគោស្រស់", "price": 15.0, "icon": "🥛"},
    {"code": "P03", "category": "សេវាកម្ម ស្ប៉ា", "name": "ឈុតស្ប៉ាដោះគោស្រស់កូនក្រមុំ", "price": 20.0, "icon": "👰"},
]

# State Initialization
if "cart" not in st.session_state:
    st.session_state.cart = []
if "sales_history" not in st.session_state:
    st.session_state.sales_history = [
        {"inv_no": "INV-1001", "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "customer": "General", "total_usd": 15.0, "total_khr": 61500, "items": [{"name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ", "qty": 1, "price": 15.0}]},
        {"inv_no": "INV-1002", "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "customer": "Srey Leak", "total_usd": 25.0, "total_khr": 102500, "items": [{"name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនVIP ពីមុខ ដល់ ក", "qty": 1, "price": 25.0}]},
    ]
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
if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None

# Navigation Menu
main_mode = st.radio("📌 Navigation Menu", ["🖥️ ផ្ទាំងលក់ (POS System)", "🧾 វិក្កយបត្រ (Last Receipt)", "📊 របាយការណ៍លក់ប្រចាំថ្ងៃ/ខែ (Sales Report)"], horizontal=True)

st.markdown("---")

# ----------------------------------------------------------------
# MODE 1: POS SYSTEM
# ----------------------------------------------------------------
if main_mode == "🖥️ ផ្ទាំងលក់ (POS System)":
    col_left, col_right = st.columns([3.2, 1.3], gap="medium")

    with col_left:
        # Search Bar
        top_c1, top_c2 = st.columns([1, 3])
        with top_c1:
            st.markdown("### 💇‍♀️ អូនឡេន SMR")
        with top_c2:
            search_query = st.text_input("Search / Barcode Scan", placeholder="[|||] ស្វែងរកតាមកូដ ឬ ឈ្មោះសេវាកម្ម...", label_visibility="collapsed")

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
                st.toast(f"បានបន្ថែម: {matched['name']}")
                st.rerun()

        # Service Tabs
        tab_gen, tab_laser, tab_spa = st.tabs(["✨ សេវាកម្មទូទៅ", "⚡ សេវាកម្ម Laser", "🧴 សេវាកម្ម ស្ប៉ា"])

        # Function Render Circle Buttons
        def render_circle_catalog(category_name):
            items = [i for i in SERVICES_CATALOG if i["category"] == category_name]
            cols = st.columns(4)
            for idx, item in enumerate(items):
                with cols[idx % 4]:
                    button_text = f"{item['icon']}\n{item['name']}\n${item['price']:.2f}"
                    if st.button(button_text, key=f"btn_{item['code']}"):
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
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        with tab_gen:
            render_circle_catalog("សេវាកម្មទូទៅ")
        with tab_laser:
            render_circle_catalog("សេវាកម្ម Laser")
        with tab_spa:
            render_circle_catalog("សេវាកម្ម ស្ប៉ា")

        st.markdown("---")
        
        # Cart Table
        st.markdown("##### 📋 បញ្ជីសេវាកម្មដែលបានជ្រើសរើស (Cart Items)")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            
            for idx, row in cart_df.iterrows():
                c_code, c_name, c_price, c_qty, c_tot = row["code"], row["name"], row["price"], row["qty"], row["total"]
                col_i1, col_i2, col_i3, col_i4, col_i5 = st.columns([1, 4, 1.5, 1.5, 1])
                col_i1.write(f"**{c_code}**")
                col_i2.write(f"{c_name}")
                col_i3.write(f"${c_price:.2f}")
                
                new_qty = col_i4.number_input("Qty", min_value=1, value=int(c_qty), key=f"qty_{c_code}_{idx}", label_visibility="collapsed")
                if new_qty != c_qty:
                    st.session_state.cart[idx]["qty"] = new_qty
                    st.session_state.cart[idx]["total"] = new_qty * c_price
                    st.rerun()
                    
                if col_i5.button("❌", key=f"del_{c_code}_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
        else:
            st.info("💡 មិនទាន់មានសេវាកម្មក្នុង Cart នៅឡើយទេ! សូមចុចលើប៊ូតុងរង្វង់ខាងលើដើម្បីជ្រើសរើសសេវាកម្ម។")

    with col_right:
        # Customer Info
        st.markdown(f"""
        <div class="customer-info-box">
            <div>👤 <b>អតិថិជន:</b> {st.session_state.customer_name}</div>
            <div>💳 <b>កូដអតិថិជន:</b> {st.session_state.customer_code}</div>
            <hr style="margin: 6px 0; border-color: rgba(255,255,255,0.3);">
            <div># <b>លេខវេន:</b> #001 | 🕒 <b>ម៉ោងចាប់ផ្តើម:</b> {datetime.now().strftime('%H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Calculations
        subtotal = sum(item["total"] for item in st.session_state.cart)
        discount_val = (subtotal * st.session_state.discount_pct) / 100
        after_discount = subtotal - discount_val
        vat_val = (after_discount * st.session_state.vat_pct) / 100
        service_charge_val = st.session_state.service_charge
        grand_total_usd = after_discount + vat_val + service_charge_val
        grand_total_khr = round(grand_total_usd * EXCHANGE_RATE)

        st.markdown("""<div class="total-summary-header">Total Summary (សរុបត្រូវបង់)</div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="total-summary-body">
            <div class="summary-row"><span>Sub Total:</span> <span>$ {subtotal:.2f}</span></div>
            <div class="summary-row"><span>Discount ({st.session_state.discount_pct}%):</span> <span>$ {discount_val:.2f}</span></div>
            <div class="summary-row"><span>VAT:</span> <span>$ {vat_val:.2f}</span></div>
            <div class="summary-row"><span>Service Charge:</span> <span>$ {service_charge_val:.2f}</span></div>
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

        # Payment Button
        st.markdown("<div class='pay-btn'>", unsafe_allow_html=True)
        if st.button("💵 PAYMENT (ទូទាត់ប្រាក់)", key="btn_pay_main", use_container_width=True):
            if not st.session_state.cart:
                st.warning("សូមជ្រើសរើសសេវាកម្មយ៉ាងហោចណាស់មួយ!")
            else:
                st.session_state.show_payment_modal = True
        st.markdown("</div>", unsafe_allow_html=True)

        # Other Actions
        st.markdown("<div class='pos-btn'>", unsafe_allow_html=True)
        b_c1, b_c2 = st.columns(2)
        with b_c1:
            if st.button("💾 Save/Hold", key="btn_hold"):
                if st.session_state.cart:
                    st.session_state.hold_list.append(st.session_state.cart.copy())
                    st.session_state.cart = []
                    st.toast("រក្សាទុក Order រួចរាល់!")
                    st.rerun()
        with b_c2:
            if st.button("📋 Hold List", key="btn_hold_list"):
                st.info(f"ចំនួន Order ដែល Hold: {len(st.session_state.hold_list)}")

        b_c3, b_c4 = st.columns(2)
        with b_c3:
            if st.button("% Discount", key="btn_discount"):
                st.session_state.show_discount_dialog = True
        with b_c4:
            if st.button("🔑 Customer", key="btn_customer"):
                st.session_state.show_customer_dialog = True

        b_c5, b_c6 = st.columns(2)
        with b_c5:
            if st.button("🗑️ Clear Cart", key="btn_clear"):
                st.session_state.cart = []
                st.session_state.discount_pct = 0.0
                st.session_state.customer_name = "General"
                st.session_state.customer_code = "N/A"
                st.rerun()
        with b_c6:
            if st.button("🖨️ Last Receipt", key="btn_reprint"):
                st.toast("កំពុងបើកវិក្កយបត្រចុងក្រោយ...")
        st.markdown("</div>", unsafe_allow_html=True)

    # Payment Dialog Box
    if st.session_state.get("show_payment_modal", False):
        st.markdown("---")
        st.markdown("### 💵 បង្អួចទូទាត់ប្រាក់ (Payment Modal)")
        p_col1, p_col2 = st.columns(2)
        paid_usd = p_col1.number_input("ប្រាក់ទទួលបាន ($)", min_value=0.0, value=float(grand_total_usd))
        paid_khr = p_col2.number_input("ប្រាក់ទទួលបាន (៛)", min_value=0, step=1000)
        
        tot_paid = paid_usd + (paid_khr / EXCHANGE_RATE)
        change_u = tot_paid - grand_total_usd
        change_k = round(change_u * EXCHANGE_RATE)
        
        st.info(f"💵 ប្រាក់អាប់ (Change): **$ {change_u:.2f}** ({change_k:,.0f} ៛)")
        
        confirm_c1, confirm_c2 = st.columns(2)
        if confirm_c1.button("✅ យល់ព្រមទូទាត់ និង បោះពុម្ពវិក្កយបត្រ", type="primary", use_container_width=True):
            inv_no = f"INV-{len(st.session_state.sales_history) + 1001}"
            receipt_data = {
                "inv_no": inv_no,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "customer": st.session_state.customer_name,
                "items": st.session_state.cart.copy(),
                "subtotal": subtotal,
                "discount": discount_val,
                "grand_total_usd": grand_total_usd,
                "grand_total_khr": grand_total_khr,
                "paid_usd": paid_usd,
                "paid_khr": paid_khr,
                "change_usd": change_u,
                "change_khr": change_k
            }
            
            st.session_state.last_receipt = receipt_data
            st.session_state.sales_history.append({
                "inv_no": inv_no,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "customer": st.session_state.customer_name,
                "total_usd": grand_total_usd,
                "total_khr": grand_total_khr,
                "items": st.session_state.cart.copy()
            })
            
            st.session_state.cart = []
            st.session_state.show_payment_modal = False
            st.session_state.discount_pct = 0.0
            st.session_state.customer_name = "General"
            st.session_state.customer_code = "N/A"
            st.success("🎉 ការទូទាត់ប្រាក់បានជោគជ័យ! បានបង្កើតវិក្កយបត្ររួចរាល់។")
            st.rerun()

        if confirm_c2.button("❌ បោះបង់", use_container_width=True):
            st.session_state.show_payment_modal = False
            st.rerun()

# ----------------------------------------------------------------
# MODE 2: RECEIPT VIEW
# ----------------------------------------------------------------
elif main_mode == "🧾 វិក្កយបត្រ (Last Receipt)":
    st.markdown("## 🧾 វិក្កយបត្រ / RECEIPT")
    if st.session_state.last_receipt:
        rc = st.session_state.last_receipt
        col_rc1, _ = st.columns([2, 1])
        with col_rc1:
            st.markdown(f"""
            <div class="receipt-container">
                <h2 style="text-align: center; margin-bottom: 5px;">💇‍♀️ អូនឡេន SMR BEAUTY</h2>
                <p style="text-align: center; font-size: 12px; margin-top: 0;">អាសយដ្ឋាន: រាជធានីភ្នំពេញ | ទូរស័ព្ទ: 012 345 678</p>
                <hr style="border-top: 1px dashed #ec4899;">
                <p><b>លេខវិក្កយបត្រ:</b> {rc['inv_no']}<br>
                <b>កាលបរិច្ឆេទ:</b> {rc['date']}<br>
                <b>អតិថិជន:</b> {rc['customer']}</p>
                <hr style="border-top: 1px dashed #ec4899;">
                <table style="width: 100%; font-size: 13px;">
                    <tr style="text-align: left; border-bottom: 1px solid #ccc;">
                        <th>បរិយាយ</th>
                        <th>ចំនួន</th>
                        <th>តម្លៃ</th>
                        <th>សរុប</th>
                    </tr>
            """, unsafe_allow_html=True)
            
            for item in rc['items']:
                st.markdown(f"""
                <tr>
                    <td>{item['name']}</td>
                    <td>{item['qty']}</td>
                    <td>${item['price']:.2f}</td>
                    <td>${item['total']:.2f}</td>
                </tr>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                </table>
                <hr style="border-top: 1px dashed #ec4899;">
                <div style="display: flex; justify-content: space-between;"><span>សរុប (Subtotal):</span> <span>${rc['subtotal']:.2f}</span></div>
                <div style="display: flex; justify-content: space-between;"><span>បញ្ចុះតម្លៃ (Discount):</span> <span>${rc['discount']:.2f}</span></div>
                <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 16px; margin-top: 5px;">
                    <span>សរុបត្រូវបង់ (Grand Total):</span> <span>${rc['grand_total_usd']:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 14px;">
                    <span>ប្រាក់រៀល (KHR):</span> <span>៛ {rc['grand_total_khr']:,}</span>
                </div>
                <hr style="border-top: 1px dashed #ec4899;">
                <div style="display: flex; justify-content: space-between;"><span>ប្រាក់ទទួលបាន ($):</span> <span>${rc['paid_usd']:.2f}</span></div>
                <div style="display: flex; justify-content: space-between;"><span>ប្រាក់អាប់ (Change $):</span> <span>${rc['change_usd']:.2f}</span></div>
                <div style="display: flex; justify-content: space-between;"><span>ប្រាក់អាប់ (Change ៛):</span> <span>៛ {rc['change_khr']:,}</span></div>
                <p style="text-align: center; margin-top: 20px; font-weight: bold;">🙏🏻 សូមអរគុណ ជូនពរសំណាងល្អ! 🙏🏻</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.button("🖨️ បោះពុម្ពវិក្កយបត្រ (Print)", on_click=lambda: st.toast("កំពុងបញ្ជូនទៅកាន់ Printer..."))
    else:
        st.info("មិនទាន់មានវិក្កយបត្រដែលបានចេញចុងក្រោយទេ។")

# ----------------------------------------------------------------
# MODE 3: SALES REPORT
# ----------------------------------------------------------------
elif main_mode == "📊 របាយការណ៍លក់ប្រចាំថ្ងៃ/ខែ (Sales Report)":
    st.markdown("## 📊 របាយការណ៍លក់ និង ទិន្នន័យចំណូល (Sales Dashboard)")
    
    df_sales = pd.DataFrame(st.session_state.sales_history)
    
    if not df_sales.empty:
        total_revenue_usd = df_sales["total_usd"].sum()
        total_revenue_khr = df_sales["total_khr"].sum()
        total_orders = len(df_sales)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <small style="color: #666;">ចំណូលសរុប ($)</small>
                <h2 style="color: #db2777; margin: 0;">$ {total_revenue_usd:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <small style="color: #666;">ចំណូលសរុប (៛)</small>
                <h2 style="color: #db2777; margin: 0;">៛ {total_revenue_khr:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <small style="color: #666;">ចំនួនប្រតិបត្តិការសរុប</small>
                <h2 style="color: #db2777; margin: 0;">{total_orders} វិក្កយបត្រ</h2>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        rep_tab1, rep_tab2 = st.tabs(["📅 របាយការណ៍ប្រចាំថ្ងៃ", "🗓️ របាយការណ៍ប្រចាំខែ"])
        
        with rep_tab1:
            st.markdown("### 📋 បញ្ជីប្រតិបត្តិការលក់ប្រចាំថ្ងៃ")
            st.dataframe(df_sales[["inv_no", "date", "customer", "total_usd", "total_khr"]], use_container_width=True)
            
        with rep_tab2:
            st.markdown("### 📈 សរុបទិន្នន័យលក់ប្រចាំខែ")
            st.bar_chart(df_sales.set_index("date")["total_usd"])
    else:
        st.info("មិនទាន់មានទិន្នន័យលក់នៅឡើយទេ។")

# Footer Bar
st.markdown("""
<div class="pos-footer-bar">
    <span><b>Outlet:</b> OunLen SMR</span> | <span><b>Shift:</b> Active</span> | <span><b>System Status:</b> Online</span>
</div>
""", unsafe_allow_html=True)
