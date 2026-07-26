import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, date

# ----------------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Professional POS & Sales Report",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching Ready POS Layout with Updated Vivid Color Palette & Larger Fonts
st.markdown("""
<style>
    /* Main Background & Base Styling */
    .stApp {
        background-color: #fdf2f8 !important; /* Soft Pink tint */
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif;
        color: #0f172a !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, div, span {
        color: #0f172a !important;
    }

    /* Top Radio Bar Styling */
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] > div {
        background-color: #ffffff !important;
        padding: 6px 12px !important;
        border-radius: 10px !important;
        border: 2px solid #f472b6 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] span {
        color: #831843 !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    /* Category Left Sidebar Tiles */
    .cat-card {
        background-color: #ffffff;
        border: 2px solid #fbcfe8;
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .cat-card:hover {
        border-color: #db2777;
        background-color: #fce7f3;
        transform: translateY(-2px);
    }
    .cat-icon { font-size: 28px; margin-bottom: 4px; }
    .cat-title { font-size: 14px; font-weight: bold; color: #831843 !important; }

    /* Service / Product Cards Grid */
    .product-card {
        background: #ffffff;
        border: 1px solid #f472b6;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 3px 6px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-card:hover {
        border-color: #db2777;
        box-shadow: 0 6px 12px rgba(219,39,119,0.15);
    }
    .product-icon { font-size: 38px; margin: 4px 0; }
    .product-title { font-size: 14px; font-weight: 700; color: #0f172a !important; height: 38px; overflow: hidden; }
    .product-code { font-size: 12px; color: #9d174d !important; font-weight: 600; }
    .product-price { font-size: 16px; font-weight: 800; color: #059669 !important; margin: 4px 0; }

    /* Custom Streamlit Buttons in Product Grid (Pink background, White text, Larger Font) */
    .add-cart-btn button {
        border-radius: 8px !important;
        width: 100% !important;
        height: 40px !important;
        background: #be185d !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 800 !important;
        border: none !important;
        padding: 0 !important;
    }
    .add-cart-btn button:hover {
        background: #9d174d !important;
        color: #fef08a !important; /* Soft yellow contrast on hover */
    }

    /* Cart Right Panel Styling */
    .cart-container {
        background: #ffffff;
        border: 2px solid #f472b6;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .payment-chip {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        font-size: 13px;
        font-weight: 700;
        color: #334155 !important;
        cursor: pointer;
    }
    .payment-chip.active {
        background: #0284c7;
        color: #ffffff !important;
        border-color: #0284c7;
    }

    /* POS Action Bar Buttons - Custom Vivid Colors & Larger Text */
    .btn-cancel button {
        background-color: #dc2626 !important; /* Dark Red */
        color: #ffffff !important;            /* White Text */
        font-weight: 800 !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 8px !important;
        height: 48px !important;
    }
    .btn-cancel button:hover {
        background-color: #b91c1c !important;
    }

    .btn-draft button {
        background-color: #d97706 !important; /* Amber / Dark Orange */
        color: #ffffff !important;            /* White Text */
        font-weight: 800 !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 8px !important;
        height: 48px !important;
    }
    .btn-draft button:hover {
        background-color: #b45309 !important;
    }

    .btn-pay button {
        background: #15803d !important;      /* Deep Green */
        color: #ffffff !important;            /* White Text */
        font-weight: 800 !important;
        font-size: 17px !important;
        border: none !important;
        border-radius: 8px !important;
        height: 48px !important;
    }
    .btn-pay button:hover {
        background: #166534 !important;
    }

    /* General Streamlit Base Buttons Overrides for high-contrast colors and larger font */
    div.stButton > button {
        font-size: 15px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }

    /* Metric Card in Sales Report */
    .metric-card {
        background-color: #ffffff;
        border: 2px solid #f472b6;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-card h4 { margin: 0; font-size: 15px; color: #831843 !important; }
    .metric-card h2 { margin: 8px 0 0 0; font-size: 26px; color: #db2777 !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. Data Initialization & Setup
# ----------------------------------------------------------------
EXCHANGE_RATE = 4100

if "categories" not in st.session_state:
    st.session_state.categories = ["✨ សេវាកម្មទូទៅ", "⚡ សេវាកម្ម Laser", "🧴 សេវាកម្ម ស្ប៉ា"]

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "ទាំងអស់ (All)"

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
    st.session_state.customer_name = "General Customer"
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
if "show_payment_modal" not in st.session_state:
    st.session_state.show_payment_modal = False
if "payment_method" not in st.session_state:
    st.session_state.payment_method = "Cash"

# ----------------------------------------------------------------
# 3. Receipt Generator
# ----------------------------------------------------------------
def generate_receipt_html(data):
    items_html = ""
    items_list = data.get('items', [])
    for item in items_list:
        items_html += f"""
        <tr>
            <td style="text-align: left; padding: 3px 0;">{item.get('name', 'N/A')}</td>
            <td style="text-align: center; padding: 3px 0;">{item.get('qty', 1)}</td>
            <td style="text-align: right; padding: 3px 0;">${item.get('price', 0.0):.2f}</td>
            <td style="text-align: right; padding: 3px 0;">${item.get('total', 0.0):.2f}</td>
        </tr>
        """

    inv_no = data.get('inv_no', 'N/A')
    date_str = data.get('date', '')
    customer = data.get('customer', 'General')
    subtotal = data.get('subtotal', 0.0)
    discount = data.get('discount', 0.0)
    grand_total_usd = data.get('grand_total_usd', data.get('total_usd', 0.0))
    grand_total_khr = data.get('grand_total_khr', round(grand_total_usd * EXCHANGE_RATE))
    paid_usd = data.get('paid_usd', 0.0)
    change_usd = data.get('change_usd', 0.0)
    change_khr = data.get('change_khr', 0)

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
                background-color: #db2777; color: white; border: none;
                padding: 12px; font-size: 15px; font-weight: bold;
                border-radius: 6px; cursor: pointer; width: 100%; margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <button class="print-btn no-print" onclick="window.print()">🖨️ ព្រីនវិក្កយបត្រ (80mm)</button>
        <div class="text-center">
            <h2 style="margin: 0; font-size: 16px;">💇‍♀️ អូនឡែន សម្រស់</h2>
            <p style="margin: 2px 0; font-size: 10px;">អស័យដ្ឋាន ភូមិដំណាក់ពពូល សង្កាត់កំពង់ឆ្នាំង ក្រុងកំពង់ឆ្នាំង </p>
            <p style="margin: 2px 0; font-size: 10px;">ទូរស័ព្ទ: 067 969 877</p>
        </div>
        <div class="dashed-line"></div>
        <div style="font-size: 10px;">
            <div class="flex-between"><span>លេខវិក្កយបត្រ:</span> <b>{inv_no}</b></div>
            <div class="flex-between"><span>កាលបរិច្ឆេទ:</span> <span>{date_str}</span></div>
            <div class="flex-between"><span>អតិថិជន:</span> <span>{customer}</span></div>
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
            <div class="flex-between"><span>សរុបរង (Subtotal):</span> <span>${subtotal:.2f}</span></div>
            <div class="flex-between"><span>បញ្ចុះតម្លៃ:</span> <span>-${discount:.2f}</span></div>
            <div class="dashed-line"></div>
            <div class="flex-between" style="font-size: 13px; font-weight: bold;">
                <span>ត្រូវបង់សរុប:</span> <span>${grand_total_usd:.2f}</span>
            </div>
            <div class="flex-between" style="font-weight: bold;">
                <span>ជាប្រាក់រៀល:</span> <span>៛ {grand_total_khr:,}</span>
            </div>
        </div>
        <div class="dashed-line"></div>
        <div style="font-size: 10px;">
            <div class="flex-between"><span>ប្រាក់ទទួលបាន ($):</span> <span>${paid_usd:.2f}</span></div>
            <div class="flex-between"><span>ប្រាក់អាប់ ($):</span> <span>${change_usd:.2f}</span></div>
            <div class="flex-between"><span>ប្រាក់អាប់ (៛):</span> <span>៛ {change_khr:,}</span></div>
        </div>
        <div class="dashed-line"></div>
        <div class="text-center" style="margin-top: 10px; font-size: 10px;">
            <p>🙏🏻 សូមអរគុណ ជូនពរសំណាងល្អ! </p>
        </div>
    </body>
    </html>
    """

# ----------------------------------------------------------------
# 4. Dialog Popups
# ----------------------------------------------------------------
@st.dialog("🎁 បញ្ចុះតម្លៃ (Apply Discount)")
def set_discount_dialog():
    st.write("បញ្ចុះតម្លៃ៖")
    new_discount = st.number_input("ភាគរយបញ្ចុះតម្លៃ (%)", min_value=0.0, max_value=100.0, value=float(st.session_state.discount_pct), step=1.0)
    col_d1, col_d2 = st.columns(2)
    if col_d1.button("✅ យល់ព្រម", type="primary", use_container_width=True):
        st.session_state.discount_pct = new_discount
        st.toast(f"បានកំណត់ការបញ្ចុះតម្លៃ: {new_discount}%")
        st.rerun()
    if col_d2.button("❌ បោះបង់", use_container_width=True):
        st.rerun()

# ----------------------------------------------------------------
# 5. Main Navigation
# ----------------------------------------------------------------
main_mode = st.radio(
    "📌 Navigation Menu", 
    ["🖥️ ផ្ទាំងលក់ (POS System)", "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)", "⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម (Categories)", "🧾 វិក្កយបត្រ (Last Receipt 80mm)", "📊 របាយការណ៍លក់ប្រចាំថ្ងៃ/ខែ (Sales Report)"], 
    horizontal=True
)

st.markdown("---")

# Helper to Add Item to Cart
def add_to_cart(item):
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

# ----------------------------------------------------------------
# MODE 1: POS SYSTEM (Redesigned matching Ready POS Layout)
# ----------------------------------------------------------------
if main_mode == "🖥️ ផ្ទាំងលក់ (POS System)":
    
    # 3-Column Layout: Categories Sidebar (1.2) | Products Grid (3.2) | Order Cart (2.4)
    col_cat, col_prod, col_cart = st.columns([1.2, 3.2, 2.4], gap="small")

    # ================= 1. LEFT PANEL: Categories Sidebar =================
    with col_cat:
        st.markdown("##### 📂 ប្រភេទ (Categories)")
        
        all_selected = (st.session_state.selected_category == "ទាំងអស់ (All)")
        if st.button("🌸 ទាំងអស់ (All)", key="cat_all", type="primary" if all_selected else "secondary", use_container_width=True):
            st.session_state.selected_category = "ទាំងអស់ (All)"
            st.rerun()

        for idx, cat_name in enumerate(st.session_state.categories):
            is_active = (st.session_state.selected_category == cat_name)
            icon = "✨" if "ទូទៅ" in cat_name else ("⚡" if "Laser" in cat_name else "🧴")
            if st.button(f"{icon} {cat_name}", key=f"cat_btn_{idx}", type="primary" if is_active else "secondary", use_container_width=True):
                st.session_state.selected_category = cat_name
                st.rerun()

    # ================= 2. CENTER PANEL: Products / Services Grid =================
    with col_prod:
        st.markdown("##### 💇‍♀️ សេវាកម្ម (Services)")
        
        # Search & Scan Bar
        search_query = st.text_input("Search / Scan Code", placeholder="[|||] ស្វែងរកតាមកូដ ឬ ឈ្មោះសេវាកម្ម...", label_visibility="collapsed")
        
        # Filter services list
        if st.session_state.selected_category == "ទាំងអស់ (All)":
            filtered_services = st.session_state.services_catalog
        else:
            filtered_services = [s for s in st.session_state.services_catalog if s["category"] == st.session_state.selected_category]

        if search_query:
            filtered_services = [s for s in filtered_services if search_query.lower() in s["name"].lower() or search_query.lower() in s["code"].lower()]

        # Display Services Grid (4 Columns)
        if not filtered_services:
            st.info("រកមិនឃើញសេវាកម្មឡើយ!")
        else:
            grid_cols = st.columns(4)
            for idx, item in enumerate(filtered_services):
                with grid_cols[idx % 4]:
                    st.markdown(f"""
                    <div class="product-card">
                        <div>
                            <div class="product-icon">{item.get('icon', '✨')}</div>
                            <div class="product-title">{item['name']}</div>
                            <div class="product-code">Code: {item['code']}</div>
                        </div>
                        <div class="product-price">${item['price']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown('<div class="add-cart-btn">', unsafe_allow_html=True)
                    if st.button("➕ បញ្ចូល Cart", key=f"add_{item['code']}_{idx}"):
                        add_to_cart(item)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.write("")

    # ================= 3. RIGHT PANEL: Cart & Checkout =================
    with col_cart:
        st.markdown("<div class='cart-container'>", unsafe_allow_html=True)
        
        # Customer Field
        c_col1, c_col2 = st.columns([4, 1])
        c_name = c_col1.text_input("Customer Name", value=st.session_state.customer_name, label_visibility="collapsed", placeholder="Enter Customer name or phone number")
        st.session_state.customer_name = c_name
        if c_col2.button("👤+", key="btn_quick_cust"):
            st.toast("បញ្ចូលឈ្មោះអតិថិជនរួចរាល់")

        # Cart Items Header & Table
        st.markdown("""
        <div style="background-color: #f8fafc; padding: 6px 10px; border-radius: 6px; border: 1px solid #e2e8f0; font-size: 12px; font-weight: bold; margin: 8px 0;">
            <div style="display: flex; justify-content: space-between;">
                <span style="width: 40%;">Product</span>
                <span style="width: 20%; text-align: center;">Price</span>
                <span style="width: 20%; text-align: center;">QTY</span>
                <span style="width: 20%; text-align: right;">Subtotal</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        subtotal = 0.0
        total_items_count = 0

        if st.session_state.cart:
            for idx, item in enumerate(st.session_state.cart):
                subtotal += item["total"]
                total_items_count += item["qty"]
                
                ic1, ic2, ic3, ic4 = st.columns([2.5, 1.2, 1.3, 1.5])
                ic1.markdown(f"<div style='font-size:12px; font-weight:bold;'>{item['name']}</div>", unsafe_allow_html=True)
                ic2.markdown(f"<div style='font-size:12px; text-align:center;'>${item['price']:.2f}</div>", unsafe_allow_html=True)
                
                # Qty selector
                new_q = ic3.number_input("qty", min_value=1, value=int(item["qty"]), key=f"cart_q_{idx}", label_visibility="collapsed")
                if new_q != item["qty"]:
                    st.session_state.cart[idx]["qty"] = new_q
                    st.session_state.cart[idx]["total"] = new_q * item["price"]
                    st.rerun()

                ic4.markdown(f"<div style='font-size:12px; text-align:right; font-weight:bold;'>${item['total']:.2f}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; padding:20px; color:#64748b; font-size:13px;'>No products available in the list</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 10px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)

        # Calculation Calculations
        discount_val = (subtotal * st.session_state.discount_pct) / 100
        grand_total_usd = subtotal - discount_val
        grand_total_khr = round(grand_total_usd * EXCHANGE_RATE)

        st.markdown(f"""
        <div style="font-size: 14px; line-height: 1.8;">
            <div style="display:flex; justify-content:space-between;">
                <span>Total Products:</span> <b>{len(st.session_state.cart)} ({total_items_count})</b>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>Total Amount:</span> <b>$ {subtotal:.2f}</b>
            </div>
            <div style="display:flex; justify-content:space-between; color:#dc2626;">
                <span>Discount ({st.session_state.discount_pct}%):</span> <b>-$ {discount_val:.2f}</b>
            </div>
            <hr style="margin:6px 0;">
            <div style="display:flex; justify-content:space-between; font-size:17px; font-weight:bold; color:#0284c7;">
                <span>Grand Total:</span> <span>$ {grand_total_usd:.2f}</span>
            </div>
            <div style="display:flex; justify-content:flex-end; font-size:14px; font-weight:bold; color:#059669;">
                <span>៛ {grand_total_khr:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

        # Payment Methods Chips
        p_cols = st.columns(4)
        methods = ["Cash", "ABA/KHQR", "Paystack", "Stripe"]
        for m_idx, method in enumerate(methods):
            with p_cols[m_idx]:
                if st.button(method, key=f"pay_meth_{m_idx}", type="primary" if st.session_state.payment_method == method else "secondary"):
                    st.session_state.payment_method = method
                    st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Action Buttons (Cancel / Draft / Pay)
        ac1, ac2, ac3 = st.columns([1, 1, 1.5])
        with ac1:
            st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
            if st.button("Cancel", key="pos_cancel", use_container_width=True):
                st.session_state.cart = []
                st.session_state.discount_pct = 0.0
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with ac2:
            st.markdown('<div class="btn-draft">', unsafe_allow_html=True)
            if st.button("Draft", key="pos_draft", use_container_width=True):
                if st.session_state.cart:
                    st.session_state.hold_list.append(st.session_state.cart.copy())
                    st.session_state.cart = []
                    st.toast("បានរក្សាទុក Draft!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with ac3:
            st.markdown('<div class="btn-pay">', unsafe_allow_html=True)
            if st.button("Save & Complete", key="pos_pay", use_container_width=True):
                if not st.session_state.cart:
                    st.warning("សូមជ្រើសរើសសេវាកម្ម!")
                else:
                    st.session_state.show_payment_modal = True
            st.markdown('</div>', unsafe_allow_html=True)

        # Quick Discount Link
        if st.button("🎁 កំណត់ Discount (%)", key="btn_open_disc", use_container_width=True):
            set_discount_dialog()

        st.markdown("</div>", unsafe_allow_html=True)

    # Payment Confirmation Modal
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
            st.session_state.customer_name = "General Customer"
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
# MODE 4: RECEIPT VIEW
# ----------------------------------------------------------------
elif main_mode == "🧾 វិក្កយបត្រ (Last Receipt 80mm)":
    st.markdown("## 🧾 ប្រវត្តិប្រតិបត្តិការ និង ការពិនិត្យវិក្កយបត្រ (80mm Thermal Paper)")
    
    if not st.session_state.sales_history:
        st.info("💡 មិនទាន់មានប្រវត្តិប្រតិបត្តិការ/ការលក់នៅឡើយទេ។ សូមធ្វើការលក់នៅលើផ្ទាំង POS ជាមុនសិន।")
    else:
        col_list, col_preview = st.columns([1.5, 1], gap="medium")

        with col_list:
            st.markdown("### 📋 បញ្ជីប្រតិបត្តិការទាំងអស់")
            df_display = []
            for idx, item in enumerate(reversed(st.session_state.sales_history)):
                total_val = item.get('grand_total_usd', item.get('total_usd', 0.0))
                df_display.append({
                    "ល.រ": len(st.session_state.sales_history) - idx,
                    "លេខវិក្កយបត្រ": item.get("inv_no", f"INV-{idx+1}"),
                    "កាលបរិច្ឆេទ": item.get("date", ""),
                    "អតិថិជន": item.get("customer", "General"),
                    "សរុប ($)": f"${total_val:.2f}"
                })
            
            st.dataframe(pd.DataFrame(df_display), use_container_width=True, hide_index=True)
            st.markdown("---")
            inv_list = [item.get("inv_no", "N/A") for item in reversed(st.session_state.sales_history)]
            selected_inv = st.selectbox("ជ្រើសរើសលេខវិក្កយបត្រដើម្បី Preview/Print:", inv_list)
            selected_receipt_data = next((item for item in st.session_state.sales_history if item.get("inv_no") == selected_inv), None)

        with col_preview:
            st.markdown("### 👁️ មើលគំរូវិក្កយបត្រ")
            if selected_receipt_data:
                html_code = generate_receipt_html(selected_receipt_data)
                components.html(html_code, height=520, scrolling=True)

# ----------------------------------------------------------------
# MODE 5: SALES REPORT DASHBOARD
# ----------------------------------------------------------------
elif main_mode == "📊 របាយការណ៍លក់ប្រចាំថ្ងៃ/ខែ (Sales Report)":
    st.markdown("## 📊 របាយការណ៍លក់ប្រចាំថ្ងៃ/ខែ (Sales Analytics)")

    if not st.session_state.sales_history:
        st.info("💡 មិនទាន់មានទិន្នន័យលក់សម្រាប់បង្ហាញរបាយការណ៍នៅឡើយទេ!")
    else:
        # Overview Cards
        total_invoices = len(st.session_state.sales_history)
        total_revenue_usd = sum(item.get("grand_total_usd", 0.0) for item in st.session_state.sales_history)
        total_revenue_khr = round(total_revenue_usd * EXCHANGE_RATE)

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🧾 ចំនួនវិក្កយបត្រសរុប</h4>
                <h2>{total_invoices}</h2>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>💵 ចំណូលសរុប ($)</h4>
                <h2>${total_revenue_usd:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>៛ ចំណូលសរុប (៛)</h4>
                <h2>៛ {total_revenue_khr:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Extract Item level details for deep analytics
        item_rows = []
        for sale in st.session_state.sales_history:
            inv = sale.get("inv_no")
            dt = sale.get("date")
            cust = sale.get("customer")
            for it in sale.get("items", []):
                item_rows.append({
                    "Invoice": inv,
                    "Date": dt,
                    "Customer": cust,
                    "Code": it.get("code"),
                    "Service Name": it.get("name"),
                    "Price": it.get("price"),
                    "Qty": it.get("qty"),
                    "Subtotal": it.get("total")
                })

        df_items = pd.DataFrame(item_rows)

        st.markdown("### 🏆 សេវាកម្មលក់ដាច់បំផុត (Popular Services)")
        if not df_items.empty:
            summary_df = df_items.groupby(["Code", "Service Name"]).agg(
                Total_Qty=("Qty", "sum"),
                Total_Revenue=("Subtotal", "sum")
            ).reset_index().sort_values(by="Total_Qty", ascending=False)
            
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.markdown("### 📑 បញ្ជីលម្អិតនៃការលក់ទាំងអស់")
        st.dataframe(df_items, use_container_width=True, hide_index=True)
