import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
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

# Custom CSS for UI Enhancement
st.markdown("""
<style>
    .stApp {
        background-color: #fdf2f8 !important;
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif;
        color: #0f172a;
    }
    
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
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] input:checked + div {
        background-color: #db2777 !important;
    }

    button[data-baseweb="tab"] p {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    button[aria-selected="true"] p {
        color: #db2777 !important;
        font-weight: bold !important;
    }

    /* Circle Button Styling */
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

    .customer-info-box {
        background-color: #047857;
        color: #ffffff;
        padding: 14px 16px;
        border-radius: 8px 8px 0px 0px;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

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

if "categories" not in st.session_state:
    st.session_state.categories = ["✨ សេវាកម្មទូទៅ", "⚡ សេវាកម្ម Laser", "🧴 សេវាកម្ម ស្ប៉ា"]

if "services_catalog" not in st.session_state:
    st.session_state.services_catalog = [
        {"code": "S01", "category": "✨ សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ", "price": 15.0, "icon": "🌿"},
        {"code": "S02", "category": "✨ សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីន baby Glow", "price": 15.0, "icon": "✨"},
        {"code": "S03", "category": "✨ សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីន college", "price": 12.5, "icon": "💧"},
        {"code": "S04", "category": "✨ សេវាកម្មទូទៅ", "name": "ញេចសម្អាតគ្រាប់មុន ជម្រុះកោសិកា", "price": 7.5, "icon": "🧖‍♀️"},
        {"code": "S05", "category": "✨ សេវាកម្មទូទៅ", "name": "ម៉ាសស្កាតបញ្ចូលវីតាមីនVIP ពីមុខ ដល់ ក", "price": 25.0, "icon": "👑"},
        {"code": "S06", "category": "✨ សេវាកម្មទូទៅ", "name": "កក់សក់ + បិទម៉ាស", "price": 4.0, "icon": "💇‍♀️"},
        {"code": "L01", "category": "⚡ សេវាកម្ម Laser", "name": "បាញ់ Laser ក្លៀក", "price": 5.0, "icon": "⚡"},
        {"code": "L02", "category": "⚡ សេវាកម្ម Laser", "name": "បាញ់ Laser រោមដៃ", "price": 9.0, "icon": "⚡"},
        {"code": "P01", "category": "🧴 សេវាកម្ម ស្ប៉ា", "name": "ឈុតស្ប៉ាស្បែក", "price": 10.0, "icon": "🧴"},
        {"code": "P02", "category": "🧴 សេវាកម្ម ស្ប៉ា", "name": "ឈុតស្ប៉ាដោះគោស្រស់", "price": 15.0, "icon": "🥛"},
    ]

if "cart" not in st.session_state:
    st.session_state.cart = []
if "sales_history" not in st.session_state:
    st.session_state.sales_history = []
if "customer_name" not in st.session_state:
    st.session_state.customer_name = "General"
if "customer_code" not in st.session_state:
    st.session_state.customer_code = "N/A"
if "discount_pct" not in st.session_state:
    st.session_state.discount_pct = 0.0
if "vat_pct" not in st.session_state:
    st.session_state.vat_pct = 0.0
if "hold_list" not in st.session_state:
    st.session_state.hold_list = []
if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None

# ----------------------------------------------------------------
# 3. Function Generator - 80mm HTML Receipt Component
# ----------------------------------------------------------------
def generate_receipt_html(data):
    items_html = ""
    for item in data['items']:
        items_html += f"""
        <tr>
            <td style="text-align: left; padding: 3px 0;">{item['name']}</td>
            <td style="text-align: center; padding: 3px 0;">{item['qty']}</td>
            <td style="text-align: right; padding: 3px 0;">${item['price']:.2f}</td>
            <td style="text-align: right; padding: 3px 0;">${item['total']:.2f}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: 80mm auto; margin: 0; }}
            body {{
                font-family: 'Kantumruy Pro', 'Khmer OS Battambang', monospace;
                width: 72mm;
                margin: 0 auto;
                padding: 5px;
                background-color: #ffffff;
                color: #000000;
                font-size: 12px;
            }}
            .text-center {{ text-align: center; }}
            .dashed-line {{ border-top: 1px dashed #000; margin: 6px 0; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
            .flex-between {{ display: flex; justify-content: space-between; margin: 2px 0; }}
            @media print {{ .no-print {{ display: none !important; }} body {{ width: 100%; }} }}
            .print-btn {{
                background-color: #059669; color: white; border: none;
                padding: 10px; font-size: 14px; font-weight: bold;
                border-radius: 6px; cursor: pointer; width: 100%; margin-bottom: 10px;
            }}
            .print-btn:hover {{ background-color: #047857; }}
        </style>
    </head>
    <body>
        <button class="print-btn no-print" onclick="window.print()">🖨️ ចុចទីនេះដើម្បី ព្រីនវិក្កយបត្រ (80mm)</button>
        <div class="text-center">
            <h2 style="margin: 0; font-size: 16px;">💇‍♀️ អូនឡេន SMR BEAUTY</h2>
            <p style="margin: 2px 0; font-size: 10px;">សាខាទី ១: រាជធានីភ្នំពេញ</p>
            <p style="margin: 2px 0; font-size: 10px;">ទូរស័ព្ទ: 012 345 678</p>
        </div>
        <div class="dashed-line"></div>
        <div style="font-size: 10px;">
            <div class="flex-between"><span>លេខវិក្កយបត្រ:</span> <b>{data['inv_no']}</b></div>
            <div class="flex-between"><span>កាលបរិច្ឆេទ:</span> <span>{data['date']}</span></div>
            <div class="flex-between"><span>អតិថិជន:</span> <span>{data['customer']}</span></div>
        </div>
        <div class="dashed-line"></div>
        <table>
            <thead>
                <tr style="border-bottom: 1px solid #000;">
                    <th style="text-align: left;">សេវាកម្ម</th>
                    <th style="text-align: center;">ចំនួន</th>
                    <th style="text-align: right;">តម្លៃ</th>
                    <th style="text-align: right;">សរុប</th>
                </tr>
            </thead>
            <tbody>{items_html}</tbody>
        </table>
        <div class="dashed-line"></div>
        <div style="font-size: 11px;">
            <div class="flex-between"><span>សរុបរង (Subtotal):</span> <span>${data.get('subtotal', 0):.2f}</span></div>
            <div class="flex-between"><span>បញ្ចុះតម្លៃ:</span> <span>-${data.get('discount', 0):.2f}</span></div>
            <div class="dashed-line"></div>
            <div class="flex-between" style="font-size: 13px; font-weight: bold;">
                <span>ត្រូវបង់សរុប:</span> <span>${data['grand_total_usd']:.2f}</span>
            </div>
            <div class="flex-between" style="font-weight: bold;">
                <span>ជាប្រាក់រៀល:</span> <span>៛ {data['grand_total_khr']:,}</span>
            </div>
        </div>
        <div class="dashed-line"></div>
        <div style="font-size: 10px;">
            <div class="flex-between"><span>ប្រាក់ទទួលបាន ($):</span> <span>${data.get('paid_usd', 0):.2f}</span></div>
            <div class="flex-between"><span>ប្រាក់អាប់ ($):</span> <span>${data.get('change_usd', 0):.2f}</span></div>
            <div class="flex-between"><span>ប្រាក់អាប់ (៛):</span> <span>៛ {data.get('change_khr', 0):,}</span></div>
        </div>
        <div class="dashed-line"></div>
        <div class="text-center" style="margin-top: 10px; font-size: 10px;">
            <p>🙏🏻 សូមអរគុណ ជូនពរសំណាងល្អ! 🙏🏻</p>
        </div>
    </body>
    </html>
    """

# ----------------------------------------------------------------
# 4. Popup Dialogs
# ----------------------------------------------------------------
@st.dialog("🎁 បញ្ចុះតម្លៃ (Apply Discount)")
def set_discount_dialog():
    st.write("សូមបញ្ចូលភាគរយ % ដែលត្រូវបញ្ចុះតម្លៃ៖")
    new_discount = st.number_input(
        "ភាគរយបញ្ចុះតម្លៃ (%)", 
        min_value=0.0, 
        max_value=100.0, 
        value=float(st.session_state.discount_pct), 
        step=1.0
    )
    col_d1, col_d2 = st.columns(2)
    if col_d1.button("✅ យល់ព្រម", type="primary", use_container_width=True):
        st.session_state.discount_pct = new_discount
        st.toast(f"បានកំណត់ការបញ្ចុះតម្លៃ: {new_discount}%")
        st.rerun()
    if col_d2.button("❌ បោះបង់", use_container_width=True):
        st.rerun()

@st.dialog("👤 កំណត់ព័ត៌មានអតិថិជន")
def set_customer_dialog():
    c_name = st.text_input("ឈ្មោះអតិថិជន:", value=st.session_state.customer_name)
    c_code = st.text_input("កូដអតិថិជន / លេខទូរស័ព្ទ:", value=st.session_state.customer_code)
    col_c1, col_c2 = st.columns(2)
    if col_c1.button("✅ រក្សាទុក", type="primary", use_container_width=True):
        st.session_state.customer_name = c_name.strip() if c_name.strip() else "General"
        st.session_state.customer_code = c_code.strip() if c_code.strip() else "N/A"
        st.toast("បានធ្វើបច្ចុប្បន្នភាពព័ត៌មានអតិថិជន!")
        st.rerun()
    if col_c2.button("❌ បោះបង់", use_container_width=True):
        st.rerun()

# ----------------------------------------------------------------
# 5. Navigation Menu
# ----------------------------------------------------------------
main_mode = st.radio(
    "📌 Navigation Menu", 
    ["🖥️ ផ្ទាំងលក់ (POS System)", "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)", "⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម (Categories)", "🧾 វិក្កយបត្រ (Last Receipt 80mm)", "📊 របាយការណ៍លក់ប្រចាំថ្ងៃ/ខែ (Sales Report)"], 
    horizontal=True
)

st.markdown("---")

# ----------------------------------------------------------------
# MODE 1: POS SYSTEM
# ----------------------------------------------------------------
if main_mode == "🖥️ ផ្ទាំងលក់ (POS System)":
    col_left, col_right = st.columns([3.2, 1.3], gap="medium")

    with col_left:
        top_c1, top_c2 = st.columns([1, 3])
        with top_c1:
            st.markdown("### 💇‍♀️ អូនឡេន SMR")
        with top_c2:
            search_query = st.text_input("Search / Barcode Scan", placeholder="[|||] ស្វែងរកតាមកូដ ឬ ឈ្មោះសេវាកម្ម...", label_visibility="collapsed")

        if search_query:
            matched = next((item for item in st.session_state.services_catalog if item["code"].lower() == search_query.strip().lower() or search_query.strip().lower() in item["name"].lower()), None)
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

        if st.session_state.categories:
            category_tabs = st.tabs(st.session_state.categories)

            def render_circle_catalog(category_name):
                items = [i for i in st.session_state.services_catalog if i["category"] == category_name]
                if not items:
                    st.info("មិនទាន់មានសេវាកម្មនៅក្នុងប្រភេទនេះទេ។")
                    return
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

            for idx, cat_name in enumerate(st.session_state.categories):
                with category_tabs[idx]:
                    render_circle_catalog(cat_name)

        st.markdown("---")
        st.markdown("##### 📋 បញ្ជីសេវាកម្មដែលបានជ្រើសរើស (Cart Items)")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            for idx, row in cart_df.iterrows():
                c_code, c_name, c_price, c_qty = row["code"], row["name"], row["price"], row["qty"]
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
            st.info("💡 មិនទាន់មានសេវាកម្មក្នុង Cart នៅឡើយទេ!")

    with col_right:
        st.markdown(f"""
        <div class="customer-info-box">
            <div>👤 <b>អតិថិជន:</b> {st.session_state.customer_name}</div>
            <div>💳 <b>កូដអតិថិជន:</b> {st.session_state.customer_code}</div>
            <hr style="margin: 6px 0; border-color: rgba(255,255,255,0.3);">
            <div># <b>លេខវេន:</b> #001 | 🕒 <b>ម៉ោង:</b> {datetime.now().strftime('%H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)

        subtotal = sum(item["total"] for item in st.session_state.cart)
        discount_val = (subtotal * st.session_state.discount_pct) / 100
        after_discount = subtotal - discount_val
        vat_val = (after_discount * st.session_state.vat_pct) / 100
        grand_total_usd = after_discount + vat_val
        grand_total_khr = round(grand_total_usd * EXCHANGE_RATE)

        st.markdown("""<div class="total-summary-header">Total Summary (សរុបត្រូវបង់)</div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="total-summary-body">
            <div class="summary-row"><span>Sub Total:</span> <span>$ {subtotal:.2f}</span></div>
            <div class="summary-row"><span>Discount ({st.session_state.discount_pct}%):</span> <span>-$ {discount_val:.2f}</span></div>
            <hr style="margin: 6px 0; border-top: 1px dashed #ccc;">
            <div class="summary-row" style="align-items: baseline;">
                <span style="font-weight:bold;">Grand Total:</span> 
                <span class="grand-total-usd">$ {grand_total_usd:.2f}</span>
            </div>
            <div class="summary-row" style="justify-content: flex-end;">
                <span class="grand-total-khr">៛ {grand_total_khr:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        st.markdown("<div class='pay-btn'>", unsafe_allow_html=True)
        if st.button("💵 PAYMENT (ទូទាត់ប្រាក់)", key="btn_pay_main", use_container_width=True):
            if not st.session_state.cart:
                st.warning("សូមជ្រើសរើសសេវាកម្មយ៉ាងហោចណាស់មួយ!")
            else:
                st.session_state.show_payment_modal = True
        st.markdown("</div>", unsafe_allow_html=True)

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
                set_discount_dialog()
        with b_c4:
            if st.button("🔑 Customer", key="btn_customer"):
                set_customer_dialog()

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
                st.toast("បើកមើលវិក្កយបត្រចុងក្រោយលើ Tab 'Receipt'")
        st.markdown("</div>", unsafe_allow_html=True)

    # Payment Modal Dynamic Display
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
        if confirm_c1.button("✅ យល់ព្រមទូទាត់ និង បង្កើតវិក្កយបត្រ", type="primary", use_container_width=True):
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
            st.session_state.sales_history.append(receipt_data)
            
            st.session_state.cart = []
            st.session_state.show_payment_modal = False
            st.session_state.discount_pct = 0.0
            st.session_state.customer_name = "General"
            st.session_state.customer_code = "N/A"
            st.success("🎉 ការទូទាត់ប្រាក់បានជោគជ័យ!")
            st.rerun()

        if confirm_c2.button("❌ បោះបង់", use_container_width=True):
            st.session_state.show_payment_modal = False
            st.rerun()

# ----------------------------------------------------------------
# MODE 2: SERVICE MANAGEMENT
# ----------------------------------------------------------------
elif main_mode == "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)":
    st.markdown("## 🛠️ គ្រប់គ្រងសេវាកម្ម (Manage Services)")
    col_s_add, col_s_edit = st.columns(2, gap="large")
    
    with col_s_add:
        st.markdown("### ➕ បន្ថែមសេវាកម្មថ្មី")
        with st.form("add_service_form", clear_on_submit=True):
            s_code = st.text_input("កូដសេវាកម្ម (Service Code)", placeholder="ឧទាហរណ៍: S10, L07...")
            s_name = st.text_input("ឈ្មោះសេវាកម្ម (Service Name)", placeholder="ឧទាហរណ៍: ម៉ាសស្កាតមុខកូនក្រមុំ")
            s_cat = st.selectbox("ជ្រើសរើសប្រភេទសេវាកម្ម", st.session_state.categories)
            s_price = st.number_input("តម្លៃ ($)", min_value=0.0, value=10.0, step=0.5)
            s_icon = st.text_input("រូបតំណាង (Emoji Icon)", value="✨")
            
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
                        "icon": s_icon.strip() if s_icon.strip() else "✨"
                    }
                    st.session_state.services_catalog.append(new_item)
                    st.success(f"បានបន្ថែមសេវាកម្ម '{s_name}' រួចរាល់!")
                    st.rerun()

    with col_s_edit:
        st.markdown("### ✏️ កែប្រែ ឬ លុបសេវាកម្ម")
        if st.session_state.services_catalog:
            service_options = [f"{item['code']} - {item['name']}" for item in st.session_state.services_catalog]
            selected_s_option = st.selectbox("ជ្រើសរើសសេវាកម្ម:", service_options)
            
            selected_code = selected_s_option.split(" - ")[0]
            target_item = next((item for item in st.session_state.services_catalog if item["code"] == selected_code), None)
            
            if target_item:
                with st.form("edit_service_form"):
                    edit_name = st.text_input("ឈ្មោះសេវាកម្ម:", value=target_item["name"])
                    edit_price = st.number_input("តម្លៃ ($):", min_value=0.0, value=float(target_item["price"]), step=0.5)
                    
                    e_col1, e_col2 = st.columns(2)
                    submit_edit_s = e_col1.form_submit_button("✏️ រក្សាទុក", type="primary")
                    submit_del_s = e_col2.form_submit_button("🗑️ លុបសេវាកម្ម")
                    
                    if submit_edit_s:
                        target_item["name"] = edit_name.strip()
                        target_item["price"] = float(edit_price)
                        st.success("បានកែប្រែសេវាកម្មរួចរាល់!")
                        st.rerun()
                        
                    if submit_del_s:
                        st.session_state.services_catalog = [item for item in st.session_state.services_catalog if item["code"] != selected_code]
                        st.success("បានលុបសេវាកម្មរួចរាល់!")
                        st.rerun()

# ----------------------------------------------------------------
# MODE 3: CATEGORY MANAGEMENT
# ----------------------------------------------------------------
elif main_mode == "⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម (Categories)":
    st.markdown("## ⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម")
    new_cat_name = st.text_input("ឈ្មោះប្រភេទសេវាកម្មថ្មី:")
    if st.button("➕ បន្ថែមប្រភេទ", type="primary"):
        if new_cat_name.strip() and new_cat_name not in st.session_state.categories:
            st.session_state.categories.append(new_cat_name.strip())
            st.success("បានបន្ថែមជោគជ័យ!")
            st.rerun()

# ----------------------------------------------------------------
# MODE 4: RECEIPT VIEW & TRANSACTION HISTORY
# ----------------------------------------------------------------
elif main_mode == "🧾 វិក្កយបត្រ (Last Receipt 80mm)":
    st.markdown("## 🧾 ប្រវត្តិប្រតិបត្តិការ និង ការពិនិត្យវិក្កយបត្រ (80mm Thermal Paper)")
    
    if not st.session_state.sales_history:
        st.info("💡 មិនទាន់មានប្រវត្តិប្រតិបត្តិការ/ការលក់នៅឡើយទេ។ សូមធ្វើការលក់នៅលើផ្ទាំង POS ជាមុនសិន។")
    else:
        col_list, col_preview = st.columns([1.5, 1], gap="medium")

        with col_list:
            st.markdown("### 📋 បញ្ជីប្រតិបត្តិការទាំងអស់")
            
            # បង្កើត DataFrame បង្ហាញតារាង
            df_display = []
            for idx, item in enumerate(reversed(st.session_state.sales_history)):
                df_display.append({
                    "ល.រ": len(st.session_state.sales_history) - idx,
                    "លេខវិក្កយបត្រ": item.get("inv_no", f"INV-{idx+1}"),
                    "កាលបរិច្ឆេទ": item.get("date", ""),
                    "អតិថិជន": item.get("customer", "General"),
                    "សរុប ($)": f"${item.get('grand_total_usd', item.get('total_usd', 0)):.2f}"
                })
            
            st.dataframe(pd.DataFrame(df_display), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("👉 **ជ្រើសរើសវិក្កយបត្រដើម្បីពិនិត្យ ឬ ព្រីនឡើងវិញ (Select Receipt to Preview/Print):**")
            
            # Selectbox សម្រាប់ជ្រើសរើសវិក្កយបត្រតាម លេខ INV-xxx
            inv_list = [item["inv_no"] for item in reversed(st.session_state.sales_history)]
            selected_inv = st.selectbox("ជ្រើសរើសលេខវិក្កយបត្រ:", inv_list)

            # ស្វែងរកទិន្នន័យនៃ Transaction ដែលបានជ្រើសរើស
            selected_receipt_data = next((item for item in st.session_state.sales_history if item["inv_no"] == selected_inv), None)

        with col_preview:
            st.markdown("### 👁️ Receipt Preview")
            if selected_receipt_data:
                receipt_payload = {
                    "inv_no": selected_receipt_data.get("inv_no", "N/A"),
                    "date": selected_receipt_data.get("date", ""),
                    "customer": selected_receipt_data.get("customer", "General"),
                    "items": selected_receipt_data.get("items", []),
                    "subtotal": selected_receipt_data.get("subtotal", selected_receipt_data.get("grand_total_usd", 0)),
                    "discount": selected_receipt_data.get("discount", 0.0),
                    "grand_total_usd": selected_receipt_data.get("grand_total_usd", 0),
                    "grand_total_khr": selected_receipt_data.get("grand_total_khr", 0),
                    "paid_usd": selected_receipt_data.get("paid_usd", selected_receipt_data.get("grand_total_usd", 0)),
                    "paid_khr": selected_receipt_data.get("paid_khr", 0),
                    "change_usd": selected_receipt_data.get("change_usd", 0.0),
                    "change_khr": selected_receipt_data.get("change_khr", 0)
                }
                
                # បង្ហាញ Receipt Preview
                rc_html = generate_receipt_html(receipt_payload)
                components.html(rc_html, height=620, scrolling=True)

# ----------------------------------------------------------------
# MODE 5: SALES REPORT
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# MODE 5: SALES REPORT WITH FIXED TOTAL CALCULATION
# ----------------------------------------------------------------
elif main_mode == "📊 របាយការណ៍លក់ប្រចាំថ្ងៃ/ខែ (Sales Report)":
    st.markdown("## 📊 របាយការណ៍លក់ និង ទិន្នន័យចំណូល")
    
    if not st.session_state.sales_history:
        st.info("💡 មិនទាន់មានទិន្នន័យលក់នៅឡើយទេ។ សូមធ្វើការលក់នៅលើផ្ទាំង POS ជាមុនសិន।")
    else:
        # Date Filter
        filter_col1, _ = st.columns([1.5, 2.5])
        with filter_col1:
            today = datetime.now().date()
            date_range = st.date_input("📅 ជ្រើសរើសចន្លោះកាលបរិច្ឆេទ (Date Range):", value=(today, today), key="sales_date_range")

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        elif isinstance(date_range, tuple) and len(date_range) == 1:
            start_date = end_date = date_range[0]
        else:
            start_date = end_date = today

        filtered_sales = []
        for item in st.session_state.sales_history:
            item_date_str = item.get("date", "")
            try:
                item_date = datetime.strptime(item_date_str, "%Y-%m-%d %H:%M:%S").date()
            except ValueError:
                try:
                    item_date = datetime.strptime(item_date_str.split(" ")[0], "%Y-%m-%d").date()
                except Exception:
                    item_date = today

            if start_date <= item_date <= end_date:
                filtered_sales.append(item)

        st.markdown("---")

        if not filtered_sales:
            st.warning(f"⚠️ មិនមានទិន្នន័យលក់ចន្លោះពីថ្ងៃ {start_date} ដល់ {end_date} ទេ។")
        else:
            # 1. គណនាចំណូលសរុប ដោយមានការត្រួតពិនិត្យ Key យ៉ាងច្បាស់លាស់ (Robust Total Calculation)
            total_invoices = len(filtered_sales)
            
            total_subtotal = 0.0
            total_discount = 0.0
            total_grand_usd = 0.0
            total_grand_khr = 0.0

            for item in filtered_sales:
                sub = float(item.get("subtotal", 0.0))
                disc = float(item.get("discount", 0.0))
                
                # ស្វែងរកតម្លៃ Grand Total USD (ប្រសិនបើគ្មាន Key grand_total_usd វានឹងយក grand_total ឬ subtotal - discount)
                gt_usd = item.get("grand_total_usd", item.get("grand_total", sub - disc))
                gt_usd = float(gt_usd) if gt_usd is not None else 0.0
                
                # ស្វែងរកតម្លៃ Grand Total KHR
                gt_khr = item.get("grand_total_khr", round(gt_usd * EXCHANGE_RATE))
                gt_khr = float(gt_khr) if gt_khr is not None else 0.0

                total_subtotal += sub
                total_discount += disc
                total_grand_usd += gt_usd
                total_grand_khr += gt_khr

            # បង្ហាញ Metric Cards ពណ៌លេចច្បាស់
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🧾 វិក្កយបត្រសរុប", f"{total_invoices} វិក្កយបត្រ")
            m2.metric("💵 ចំណូលសរុប ($)", f"${total_grand_usd:,.2f}")
            m3.metric("🎁 បញ្ចុះតម្លៃសរុប ($)", f"${total_discount:,.2f}")
            m4.metric("៛ ចំណូលសរុប (KHR)", f"៛ {total_grand_khr:,.0f}")

            st.markdown("---")

            col_rep_table, col_rep_preview = st.columns([1.5, 1], gap="medium")

            with col_rep_table:
                st.markdown(f"### 📋 បញ្ជីប្រតិបត្តិការ ({total_invoices} វិក្កយបត្រ)")
                
                report_data = []
                for idx, item in enumerate(reversed(filtered_sales)):
                    sub = float(item.get("subtotal", 0.0))
                    disc = float(item.get("discount", 0.0))
                    gt_usd = float(item.get("grand_total_usd", item.get("grand_total", sub - disc)))
                    gt_khr = float(item.get("grand_total_khr", round(gt_usd * EXCHANGE_RATE)))

                    report_data.append({
                        "ល.រ": total_invoices - idx,
                        "Invoice No": item.get("inv_no", "N/A"),
                        "Date": item.get("date", ""),
                        "Customer": item.get("customer", "General"),
                        "Subtotal ($)": f"${sub:.2f}",
                        "Discount ($)": f"${disc:.2f}",
                        "Grand Total ($)": f"${gt_usd:.2f}",
                        "Grand Total (KHR)": f"៛{gt_khr:,.0f}"
                    })

                # បន្ទាត់ចំណូលសរុប (Summary Row) នៅបាតតារាង
                report_data.append({
                    "ល.រ": "សរុប",
                    "Invoice No": f"សរុប {total_invoices} វិក្កយបត្រ",
                    "Date": "-",
                    "Customer": "-",
                    "Subtotal ($)": f"${total_subtotal:,.2f}",
                    "Discount ($)": f"${total_discount:,.2f}",
                    "Grand Total ($)": f"${total_grand_usd:,.2f}",
                    "Grand Total (KHR)": f"៛{total_grand_khr:,.0f}"
                })

                st.dataframe(pd.DataFrame(report_data), use_container_width=True, hide_index=True)

                st.markdown("---")
                filtered_inv_list = [item.get("inv_no", "N/A") for item in reversed(filtered_sales)]
                selected_rep_inv = st.selectbox("🔍 ជ្រើសរើសលេខវិក្កយបត្រដើម្បីមើលទម្រង់ 80mm / ព្រីន:", filtered_inv_list, key="select_report_inv")
                selected_rep_data = next((item for item in filtered_sales if item.get("inv_no") == selected_rep_inv), None)

            with col_rep_preview:
                st.markdown("### 🧾 វិក្កយបត្រ Preview (80mm)")
                if selected_rep_data:
                    sub = float(selected_rep_data.get("subtotal", 0.0))
                    disc = float(selected_rep_data.get("discount", 0.0))
                    gt_usd = float(selected_rep_data.get("grand_total_usd", selected_rep_data.get("grand_total", sub - disc)))
                    gt_khr = float(selected_rep_data.get("grand_total_khr", round(gt_usd * EXCHANGE_RATE)))

                    receipt_payload = {
                        "inv_no": selected_rep_data.get("inv_no", "N/A"),
                        "date": selected_rep_data.get("date", ""),
                        "customer": selected_rep_data.get("customer", "General"),
                        "items": selected_rep_data.get("items", []),
                        "subtotal": sub,
                        "discount": disc,
                        "grand_total_usd": gt_usd,
                        "grand_total_khr": gt_khr,
                        "paid_usd": selected_rep_data.get("paid_usd", gt_usd),
                        "paid_khr": selected_rep_data.get("paid_khr", 0),
                        "change_usd": selected_rep_data.get("change_usd", 0.0),
                        "change_khr": selected_rep_data.get("change_khr", 0)
                    }
                    rc_html = generate_receipt_html(receipt_payload)
                    components.html(rc_html, height=620, scrolling=True)
