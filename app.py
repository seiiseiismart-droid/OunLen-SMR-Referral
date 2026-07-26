import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration & Custom Pink Theme CSS
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Professional POS & Sales Report",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 1. Background ពណ៌ទឹកផ្កាឈូក */
    .stApp {
        background-color: #fce7f3 !important;
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif;
        color: #0f172a !important;
    }
    
    /* 2. ពណ៌អក្សរ Heading & Label ទូទៅ */
    h1, h2, h3, h4, h5, h6, label, p, span {
        color: #0f172a !important;
    }

    /* 3. Radio / Navigation Menu Top Bar */
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] > div {
        background-color: #be185d !important; /* ពណ៌ផ្កាឈូកចាស់ដិត */
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
        background-color: #831843 !important;
    }

    /* 4. Circle Buttons (POS Products) */
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
        background: #831843 !important;
        color: #ffffff !important;
        border: 1px solid #9d174d !important;
        font-size: 13px !important;
        font-weight: 600 !important;
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
    }

    /* 5. Metric Cards (របាយការណ៍សរុប) */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #be185d !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #be185d !important; /* ពណ៌លេចទិន្នន័យសរុប */
        font-size: 22px !important;
        font-weight: bold !important;
    }

    /* 6. Custom Summary Box in POS */
    .customer-info-box {
        background-color: #be185d;
        color: #ffffff !important;
        padding: 14px 16px;
        border-radius: 8px 8px 0px 0px;
        font-size: 14px;
        line-height: 1.6;
    }
    .customer-info-box div, .customer-info-box b {
        color: #ffffff !important;
    }

    .total-summary-header {
        background-color: #9d174d;
        color: #ffffff !important;
        padding: 10px 15px;
        font-weight: bold;
        font-size: 15px;
        border-radius: 8px 8px 0px 0px;
        margin-top: 10px;
    }
    
    .total-summary-body {
        background-color: #ffffff;
        border: 2px solid #be185d;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 15px;
        font-size: 13px;
        color: #0f172a !important;
        line-height: 1.8;
    }

    .summary-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }

    .pos-footer-bar {
        background-color: #be185d;
        color: #ffffff !important;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 12px;
        margin-top: 20px;
    }
    .pos-footer-bar span, .pos-footer-bar b {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. Data Initialization
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

# ----------------------------------------------------------------
# 3. Receipt HTML Generator (80mm)
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
                background-color: #be185d; color: white; border: none;
                padding: 10px; font-size: 14px; font-weight: bold;
                border-radius: 6px; cursor: pointer; width: 100%; margin-bottom: 10px;
            }}
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
            <div class="flex-between" style="font-size: 13px; font-weight: bold; color: #be185d;">
                <span>ត្រូវបង់សរុប:</span> <span>${data['grand_total_usd']:.2f}</span>
            </div>
            <div class="flex-between" style="font-weight: bold; color: #be185d;">
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
# 4. Navigation Menu
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
            <hr style="margin: 6px 0; border-color: rgba(255,255,255,0.4);">
            <div># <b>លេខវេន:</b> #001 | 🕒 <b>ម៉ោង:</b> {datetime.now().strftime('%H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)

        subtotal = sum(item["total"] for item in st.session_state.cart)
        discount_val = (subtotal * st.session_state.discount_pct) / 100
        grand_total_usd = subtotal - discount_val
        grand_total_khr = round(grand_total_usd * EXCHANGE_RATE)

        st.markdown("""<div class="total-summary-header">Total Summary (សរុបត្រូវបង់)</div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="total-summary-body">
            <div class="summary-row"><span>Sub Total:</span> <span>$ {subtotal:.2f}</span></div>
            <div class="summary-row"><span>Discount ({st.session_state.discount_pct}%):</span> <span>-$ {discount_val:.2f}</span></div>
            <hr style="margin: 6px 0; border-top: 1px dashed #ccc;">
            <div class="summary-row" style="align-items: baseline;">
                <span style="font-weight:bold;">Grand Total:</span> 
                <span style="color: #be185d; font-size: 24px; font-weight: bold;">$ {grand_total_usd:.2f}</span>
            </div>
            <div class="summary-row" style="justify-content: flex-end;">
                <span style="color: #be185d; font-size: 18px; font-weight: bold;">៛ {grand_total_khr:,.0f}</span>
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
            st.session_state.sales_history.append(receipt_data)
            st.session_state.cart = []
            st.session_state.show_payment_modal = False
            st.success("🎉 ការទូទាត់ប្រាក់បានជោគជ័យ!")
            st.rerun()

        if confirm_c2.button("❌ បោះបង់", use_container_width=True):
            st.session_state.show_payment_modal = False
            st.rerun()

# ----------------------------------------------------------------
# MODE 2: SERVICES MANAGEMENT
# ----------------------------------------------------------------
elif main_mode == "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)":
    st.markdown("## 🛠️ គ្រប់គ្រងសេវាកម្ម")

# ----------------------------------------------------------------
# MODE 3: CATEGORIES MANAGEMENT
# ----------------------------------------------------------------
elif main_mode == "⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម (Categories)":
    st.markdown("## ⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម")

# ----------------------------------------------------------------
# MODE 4: RECEIPT PREVIEW
# ----------------------------------------------------------------
elif main_mode == "🧾 វិក្កយបត្រ (Last Receipt 80mm)":
    st.markdown("## 🧾 ប្រវត្តិប្រតិបត្តិការ និង ការពិនិត្យវិក្កយបត្រ (80mm Thermal Paper)")

# ----------------------------------------------------------------
# MODE 5: SALES REPORT WITH DYNAMIC HIGH-CONTRAST METRICS
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
                item_date = today

            if start_date <= item_date <= end_date:
                filtered_sales.append(item)

        st.markdown("---")

        if not filtered_sales:
            st.warning(f"⚠️ មិនមានទិន្នន័យលក់ចន្លោះពីថ្ងៃ {start_date} ដល់ {end_date} ទេ។")
        else:
            # 1. គណនាចំណូលសរុប និងទិន្នន័យ
            total_invoices = len(filtered_sales)
            total_subtotal = sum(item.get("subtotal", 0) for item in filtered_sales)
            total_discount = sum(item.get("discount", 0) for item in filtered_sales)
            total_grand_usd = sum(item.get("grand_total_usd", 0) for item in filtered_sales)
            total_grand_khr = sum(item.get("grand_total_khr", 0) for item in filtered_sales)

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
                    report_data.append({
                        "ល.រ": total_invoices - idx,
                        "Invoice No": item.get("inv_no"),
                        "Date": item.get("date"),
                        "Customer": item.get("customer"),
                        "Subtotal ($)": f"${item.get('subtotal', 0):.2f}",
                        "Discount ($)": f"${item.get('discount', 0):.2f}",
                        "Grand Total ($)": f"${item.get('grand_total_usd', 0):.2f}",
                        "Grand Total (KHR)": f"៛{item.get('grand_total_khr', 0):,}"
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
                filtered_inv_list = [item["inv_no"] for item in reversed(filtered_sales)]
                selected_rep_inv = st.selectbox("🔍 ជ្រើសរើសលេខវិក្កយបត្រដើម្បីមើលទម្រង់ 80mm / ព្រីន:", filtered_inv_list, key="select_report_inv")
                selected_rep_data = next((item for item in filtered_sales if item["inv_no"] == selected_rep_inv), None)

            with col_rep_preview:
                st.markdown("### 🧾 វិក្កយបត្រ Preview (80mm)")
                if selected_rep_data:
                    receipt_payload = {
                        "inv_no": selected_rep_data.get("inv_no", "N/A"),
                        "date": selected_rep_data.get("date", ""),
                        "customer": selected_rep_data.get("customer", "General"),
                        "items": selected_rep_data.get("items", []),
                        "subtotal": selected_rep_data.get("subtotal", 0),
                        "discount": selected_rep_data.get("discount", 0.0),
                        "grand_total_usd": selected_rep_data.get("grand_total_usd", 0),
                        "grand_total_khr": selected_rep_data.get("grand_total_khr", 0),
                        "paid_usd": selected_rep_data.get("paid_usd", 0),
                        "paid_khr": selected_rep_data.get("paid_khr", 0),
                        "change_usd": selected_rep_data.get("change_usd", 0.0),
                        "change_khr": selected_rep_data.get("change_khr", 0)
                    }
                    rc_html = generate_receipt_html(receipt_payload)
                    components.html(rc_html, height=620, scrolling=True)

st.markdown("""
<div class="pos-footer-bar">
    <span><b>Outlet:</b> OunLen SMR</span> | <span><b>Status:</b> Ready</span>
</div>
""", unsafe_allow_html=True)
