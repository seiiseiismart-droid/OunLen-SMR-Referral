import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Professional POS & Sales Report",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS Styling
st.markdown("""
<style>
    .stApp {
        background-color: #fff1f2 !important;
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif;
        color: #0f172a !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, div, span {
        color: #0f172a !important;
    }

    /* Top Radio Menu */
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] > div {
        background-color: #ffffff !important;
        padding: 8px 14px !important;
        border-radius: 12px !important;
        border: 2px solid #f472b6 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] span {
        color: #831843 !important;
        font-size: 16px !important;
        font-weight: 800 !important;
    }

    /* Buttons base */
    .stButton > button {
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 800 !important;
        transition: all 0.2s ease-in-out !important;
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(225, 29, 72, 0.3) !important;
    }

    button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #9f1239 !important;
        border: 2px solid #f472b6 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }

    /* Product Card */
    .product-card {
        background: #ffffff;
        border: 2px solid #fda4af;
        border-radius: 14px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-card:hover {
        border-color: #e11d48;
        box-shadow: 0 8px 16px rgba(225,29,72,0.15);
    }
    .product-icon { font-size: 40px; margin: 4px 0; }
    .product-title { font-size: 15px; font-weight: 900; color: #0f172a !important; height: 40px; overflow: hidden; line-height: 1.3; }
    .product-code { font-size: 12px; color: #be123c !important; font-weight: 800; }
    .product-price { font-size: 18px; font-weight: 900; color: #047857 !important; margin: 4px 0; }

    .add-cart-btn button {
        border-radius: 10px !important;
        width: 100% !important;
        height: 42px !important;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 900 !important;
        border: none !important;
    }

    /* Cart Right Panel */
    .cart-container {
        background: #ffffff;
        border: 2px solid #f472b6;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. Data Initialization
# ----------------------------------------------------------------
EXCHANGE_RATE = 4100

if "categories" not in st.session_state:
    st.session_state.categories = ["✨ សេវាកម្មទូទៅ", "⚡ សេវាកម្ម Laser", "🧴 សេវាកម្ម ស្ប៉ា"]

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "ទាំងអស់ (All)"

if "customers_list" not in st.session_state:
    st.session_state.customers_list = [
        {"name": "General Customer", "phone": "-", "type": "Normal"},
        {"name": "អ្នកស្រី លីដា (VIP)", "phone": "012345678", "type": "VIP 10%"},
        {"name": "កញ្ញា សុភា (Gold)", "phone": "098765432", "type": "Gold Member"}
    ]

if "selected_customer" not in st.session_state:
    st.session_state.selected_customer = "General Customer"

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
    ]

if "cart" not in st.session_state:
    st.session_state.cart = []
if "sales_history" not in st.session_state:
    st.session_state.sales_history = []
if "discount_pct" not in st.session_state:
    st.session_state.discount_pct = 0.0
if "show_payment_dialog" not in st.session_state:
    st.session_state.show_payment_dialog = False
if "show_receipt_dialog" not in st.session_state:
    st.session_state.show_receipt_dialog = False
if "last_invoice" not in st.session_state:
    st.session_state.last_invoice = {}
if "last_payment_info" not in st.session_state:
    st.session_state.last_payment_info = {}

# ----------------------------------------------------------------
# 3. Helper Functions
# ----------------------------------------------------------------
def add_to_cart(item):
    existing = next((i for i in st.session_state.cart if i["code"] == item["code"]), None)
    if existing:
        existing["qty"] += 1
        recalculate_item(existing)
    else:
        st.session_state.cart.append({
            "code": item["code"],
            "name": item["name"],
            "price": item["price"],
            "qty": 1,
            "item_disc": 0.0,
            "total": item["price"]
        })

def recalculate_item(item):
    base = item["price"] * item["qty"]
    disc_amount = (base * item["item_disc"]) / 100.0
    item["total"] = base - disc_amount

def reset_pos():
    st.session_state.cart = []
    st.session_state.discount_pct = 0.0
    st.session_state.selected_customer = "General Customer"
    st.session_state.show_payment_dialog = False
    st.session_state.show_receipt_dialog = False

def generate_receipt_html(inv, pay):
    items_html = ""
    for item in inv.get('items', []):
        disc_text = f" (-{item.get('item_disc', 0)}%)" if item.get('item_disc', 0) > 0 else ""
        items_html += f"""
        <tr>
            <td style="text-align: left; padding: 4px 0;">{item.get('name', '')}{disc_text}</td>
            <td style="text-align: center; padding: 4px 0;">{item.get('qty', 1)}</td>
            <td style="text-align: right; padding: 4px 0;">${item.get('price', 0.0):.2f}</td>
            <td style="text-align: right; padding: 4px 0;">${item.get('total', 0.0):.2f}</td>
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
                background-color: #28a745; color: white; border: none;
                padding: 12px; font-size: 16px; font-weight: bold;
                border-radius: 8px; cursor: pointer; width: 100%; margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <button class="print-btn no-print" onclick="window.print()">🖨️ ព្រីនវិក្កយបត្រ (Print Receipt 80mm)</button>
        <div class="text-center">
            <h2 style="margin: 0; font-size: 16px;">💇‍♀️ អូនឡែន សម្រស់</h2>
            <p style="margin: 2px 0; font-size: 10px;">អស័យដ្ឋាន: ក្រុងកំពង់ឆ្នាំង</p>
            <p style="margin: 2px 0; font-size: 10px;">ទូរស័ព្ទ: 067 969 877</p>
        </div>
        <div class="dashed-line"></div>
        <div style="font-size: 10px;">
            <div class="flex-between"><span>លេខវិក្កយបត្រ:</span> <b>{inv.get('inv_no', 'N/A')}</b></div>
            <div class="flex-between"><span>កាលបរិច្ឆេទ:</span> <span>{inv.get('date', '')}</span></div>
            <div class="flex-between"><span>អតិថិជន:</span> <span>{inv.get('customer', 'General')}</span></div>
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
            <div class="flex-between"><span>សរុបរង (Subtotal):</span> <span>${inv.get('subtotal', 0.0):.2f}</span></div>
            <div class="flex-between"><span>បញ្ចុះតម្លៃបន្ថែម:</span> <span>-${inv.get('discount', 0.0):.2f}</span></div>
            <div class="dashed-line"></div>
            <div class="flex-between" style="font-size: 13px; font-weight: bold;">
                <span>ត្រូវបង់សរុប:</span> <span>${inv.get('grand_total_usd', 0.0):.2f}</span>
            </div>
            <div class="flex-between" style="font-weight: bold;">
                <span>ជាប្រាក់រៀល:</span> <span>៛ {round(inv.get('grand_total_usd', 0.0) * EXCHANGE_RATE):,}</span>
            </div>
        </div>
        <div class="dashed-line"></div>
        <div style="font-size: 10px;">
            <div class="flex-between"><span>ប្រាក់ទទួលបាន ($):</span> <span>${pay.get('paid_usd', 0.0):.2f}</span></div>
            <div class="flex-between"><span>ប្រាក់ទទួលបាន (៛):</span> <span>៛ {pay.get('paid_khr', 0):,}</span></div>
            <div class="flex-between"><span>ប្រាក់អាប់ ($):</span> <span>${pay.get('change_usd', 0.0):.2f}</span></div>
            <div class="flex-between"><span>ប្រាក់អាប់ (៛):</span> <span>៛ {pay.get('change_khr', 0):,}</span></div>
        </div>
        <div class="dashed-line"></div>
        <div class="text-center" style="margin-top: 10px; font-size: 10px;">
            <p>🙏🏻 សូមអរគុណ ជូនពរសំណាងល្អ!</p>
        </div>
    </body>
    </html>
    """

# ----------------------------------------------------------------
# 4. Dialogs (Pop-ups)
# ----------------------------------------------------------------
@st.dialog("👤 ចុះឈ្មោះអតិថិជនពិសេស (Add New Customer)")
def register_customer_dialog():
    st.write("បញ្ចូលព័ត៌មានអតិថិជនថ្មី៖")
    c_name = st.text_input("ឈ្មោះអតិថិជន (Name)*")
    c_phone = st.text_input("លេខទូរស័ព្ទ (Phone)")
    c_type = st.selectbox("ប្រភេទអតិថិជន (Type)", ["Normal Member", "VIP Customer (10% Off)", "Gold VIP Member"])
    
    if st.button("💾 រក្សាទុកអតិថិជន", type="primary", use_container_width=True):
        if c_name.strip():
            new_cust = {"name": c_name.strip(), "phone": c_phone.strip(), "type": c_type}
            st.session_state.customers_list.append(new_cust)
            st.session_state.selected_customer = c_name.strip()
            st.toast(f"បានចុះឈ្មោះអតិថិជន {c_name} រួចរាល់!")
            st.rerun()
        else:
            st.error("សូមបញ្ចូលឈ្មោះអតិថិជន!")

@st.dialog("🎁 កំណត់បញ្ចុះតម្លៃសរុប (Global Discount)")
def set_global_discount_dialog():
    st.write("កំណត់ភាគរយបញ្ចុះតម្លៃលើវិក្កយបត្រសរុប (%)")
    new_d = st.number_input("ភាគរយបញ្ចុះតម្លៃ (%)", min_value=0.0, max_value=100.0, value=float(st.session_state.discount_pct))
    c1, c2 = st.columns(2)
    if c1.button("✅ យល់ព្រម", type="primary", use_container_width=True):
        st.session_state.discount_pct = new_d
        st.rerun()
    if c2.button("❌ បោះបង់", use_container_width=True):
        st.rerun()

@st.dialog("💵 ផ្ទាំងទទួលប្រាក់ (Payment)", width="large")
def payment_dialog():
    total_usd = st.session_state.get("cart_total_usd", 0.0)
    total_khr = round(total_usd * EXCHANGE_RATE)

    st.write(f"### ប្រាក់ត្រូវទូទាត់សរុប: **${total_usd:,.2f}** ({total_khr:,.0f} ៛)")
    
    col1, col2 = st.columns(2)
    with col1:
        paid_usd = st.number_input("ប្រាក់ទទួលជា ដុល្លារ ($):", min_value=0.0, value=float(total_usd), step=1.0)
    with col2:
        paid_khr = st.number_input("ប្រាក់ទទួលជា រៀល (៛):", min_value=0, value=0, step=1000)

    total_paid_in_usd = paid_usd + (paid_khr / EXCHANGE_RATE)
    change_usd = total_paid_in_usd - total_usd
    change_khr = round(change_usd * EXCHANGE_RATE)

    if change_usd >= 0:
        st.success(f"💰 **ប្រាក់អាប់:** ${change_usd:,.2f} / {change_khr:,.0f} ៛")
    else:
        st.error(f"⚠️ **នៅខ្វះ:** ${abs(change_usd):,.2f} / {abs(change_khr):,.0f} ៛")

    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("❌ បោះបង់", use_container_width=True):
        st.session_state.show_payment_dialog = False
        st.rerun()

    if c2.button("✅ ទទួលប្រាក់ និងបន្តទៅវិក្កយបត្រ", type="primary", use_container_width=True):
        if change_usd < 0:
            st.error("ប្រាក់ដែលទទួលបានមិនទាន់គ្រប់ចំនួនឡើយ!")
        else:
            st.session_state.last_payment_info = {
                "paid_usd": paid_usd,
                "paid_khr": paid_khr,
                "change_usd": change_usd,
                "change_khr": change_khr
            }
            
            subtotal = sum(item["total"] for item in st.session_state.cart)
            disc_val = (subtotal * st.session_state.discount_pct) / 100.0
            
            inv_number = f"INV-{len(st.session_state.get('sales_history', [])) + 1:04d}"
            sales_data = {
                "inv_no": inv_number,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "customer": st.session_state.get("selected_customer", "General Customer"),
                "items": list(st.session_state.get("cart", [])),
                "subtotal": subtotal,
                "discount": disc_val,
                "grand_total_usd": total_usd,
                "status": "Completed"
            }
            
            st.session_state.setdefault("sales_history", []).append(sales_data)
            st.session_state.last_invoice = sales_data

            st.session_state.show_payment_dialog = False
            st.session_state.show_receipt_dialog = True
            st.rerun()

@st.dialog("🧾 វិក្កយបត្រទូទាត់ប្រាក់ (Receipt Preview)", width="large")
def receipt_dialog():
    st.success("🎉 ការទូទាត់ប្រាក់ជោគជ័យ! លោកអ្នកអាចព្រីនវិក្កយបត្រខាងក្រោមបាន។")
    
    inv = st.session_state.get("last_invoice", {})
    pay = st.session_state.get("last_payment_info", {})
    
    if inv:
        html_code = generate_receipt_html(inv, pay)
        components.html(html_code, height=450, scrolling=True)
    
    if st.button("✅ ប្រតិបត្តិការរួចរាល់ (Reset POS)", type="primary", use_container_width=True):
        reset_pos()
        st.rerun()

# Triggering dialogs based on state
if st.session_state.get("show_payment_dialog", False):
    payment_dialog()

if st.session_state.get("show_receipt_dialog", False):
    receipt_dialog()

# ----------------------------------------------------------------
# 5. Main Navigation Menu
# ----------------------------------------------------------------
main_mode = st.radio(
    "📌 Navigation Menu", 
    ["🖥️ ផ្ទាំងលក់ (POS System)", "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)", "⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម (Categories)", "🧾 វិក្កយបត្រ (Last Receipt)", "📊 របាយការណ៍លក់ (Sales Report)"], 
    horizontal=True
)

st.markdown("---")

# ================================================================
# MODE 1: POS SYSTEM
# ================================================================
if main_mode == "🖥️ ផ្ទាំងលក់ (POS System)":

    col_cat, col_prod, col_cart = st.columns([1.2, 3.2, 2.6], gap="small")

    # 1. Categories Sidebar
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

    # 2. Center Panel: Services Display
    with col_prod:
        st.markdown("##### 💇‍♀️ សេវាកម្ម (Services)")
        search_query = st.text_input("Search / Scan Code", placeholder="[|||] ស្វែងរកតាមកូដ ឬ ឈ្មោះសេវាកម្ម...", label_visibility="collapsed")
        
        filtered_services = st.session_state.services_catalog
        if st.session_state.selected_category != "ទាំងអស់ (All)":
            filtered_services = [s for s in filtered_services if s["category"] == st.session_state.selected_category]

        if search_query:
            filtered_services = [s for s in filtered_services if search_query.lower() in s["name"].lower() or search_query.lower() in s["code"].lower()]

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

    # 3. Right Panel: Cart & Actions
    with col_cart:
        st.markdown("<div class='cart-container'>", unsafe_allow_html=True)
        
        c_col1, c_col2 = st.columns([4, 1])
        cust_names = [c["name"] for c in st.session_state.customers_list]
        selected_c = c_col1.selectbox("ជ្រើសរើសអតិថិជន", cust_names, index=cust_names.index(st.session_state.selected_customer) if st.session_state.selected_customer in cust_names else 0, label_visibility="collapsed")
        st.session_state.selected_customer = selected_c
        
        if c_col2.button("👤+", key="btn_quick_cust", type="secondary"):
            register_customer_dialog()

        st.markdown("""
        <div style="background-color: #fff1f2; padding: 6px 8px; border-radius: 8px; border: 1px solid #fda4af; font-size: 12px; font-weight: 800; margin: 8px 0; color: #9f1239;">
            <div style="display: flex; justify-content: space-between;">
                <span style="width: 35%;">Service</span>
                <span style="width: 15%; text-align: center;">QTY</span>
                <span style="width: 20%; text-align: center;">Disc(%)</span>
                <span style="width: 30%; text-align: right;">Total</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        subtotal = 0.0
        total_items_count = 0

        if st.session_state.cart:
            for idx, item in enumerate(st.session_state.cart):
                ic1, ic2, ic3, ic4 = st.columns([2.2, 1.1, 1.2, 1.5])
                
                ic1.markdown(f"<div style='font-size:12px; font-weight:800; line-height:1.2;'>{item['name']}<br><small style='color:#64748b;'>${item['price']:.2f}</small></div>", unsafe_allow_html=True)
                
                new_q = ic2.number_input("qty", min_value=1, value=int(item["qty"]), key=f"cq_{idx}", label_visibility="collapsed")
                new_d = ic3.number_input("disc", min_value=0.0, max_value=100.0, value=float(item["item_disc"]), key=f"cd_{idx}", label_visibility="collapsed")
                
                if new_q != item["qty"] or new_d != item["item_disc"]:
                    item["qty"] = new_q
                    item["item_disc"] = new_d
                    recalculate_item(item)
                    st.rerun()

                ic4.markdown(f"<div style='text-align:right; font-weight:900; color:#047857; font-size:13px;'>${item['total']:.2f}</div>", unsafe_allow_html=True)
                subtotal += item["total"]
                total_items_count += item["qty"]
        else:
            st.info("🛒 កញ្ចប់ Cart នៅទទេស្អាត!")

        st.markdown("---")
        
        # Calculation display
        global_disc_val = (subtotal * st.session_state.discount_pct) / 100.0
        grand_total_usd = subtotal - global_disc_val
        grand_total_khr = round(grand_total_usd * EXCHANGE_RATE)

        st.markdown(f"""
        <div style="font-size:13px; line-height: 1.6;">
            <div style="display:flex; justify-content:space-between;"><span>សរុបរង (Subtotal):</span><b>${subtotal:,.2f}</b></div>
            <div style="display:flex; justify-content:space-between; color:#be123c;"><span>បញ្ចុះតម្លៃបន្ថែម ({st.session_state.discount_pct}%):</span><b>-${global_disc_val:,.2f}</b></div>
            <hr style="margin:6px 0;">
            <div style="display:flex; justify-content:space-between; font-size:18px; font-weight:900; color:#be123c;"><span>សរុបចុងក្រោយ:</span><b>${grand_total_usd:,.2f}</b></div>
            <div style="display:flex; justify-content:space-between; font-size:14px; font-weight:800; color:#0369a1;"><span>ជាប្រាក់រៀល:</span><b>{grand_total_khr:,.0f} ៛</b></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Action buttons
        b1, b2 = st.columns(2)
        if b1.button("🎁 ថែម Disc %", use_container_width=True):
            set_global_discount_dialog()
            
        if b2.button("❌ លុប Cart", use_container_width=True):
            st.session_state.cart = []
            st.session_state.discount_pct = 0.0
            st.rerun()

        if st.button("💵 ទូទាត់ប្រាក់ (Pay Now)", type="primary", use_container_width=True):
            if not st.session_state.cart:
                st.error("សូមជ្រើសរើសសេវាកម្មយ៉ាងហោចណាស់ 1 មុនពេលទូទាត់!")
            else:
                st.session_state.cart_total_usd = grand_total_usd
                st.session_state.show_payment_dialog = True
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ================================================================
# MODE 2 - 5: PLACEHOLDERS FOR OTHER PAGES
# ================================================================
elif main_mode == "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)":
    st.title("🛠️ គ្រប់គ្រងសេវាកម្ម (Services Management)")
    st.write("ផ្ទាំងគ្រប់គ្រង និងបន្ថែមសេវាកម្មក្នុងហាង")

elif main_mode == "⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម (Categories)":
    st.title("⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម (Categories Management)")
    st.write("ផ្ទាំងគ្រប់គ្រងប្រភេទសេវាកម្ម")

elif main_mode == "🧾 វិក្កយបត្រ (Last Receipt)":
    st.title("🧾 វិក្កយបត្រចុងក្រោយ")
    if st.session_state.last_invoice:
        html_code = generate_receipt_html(st.session_state.last_invoice, st.session_state.last_payment_info)
        components.html(html_code, height=500, scrolling=True)
    else:
        st.info("មិនទាន់មានវិក្កយបត្រដែលបានចេញនៅឡើយទេ!")

elif main_mode == "📊 របាយការណ៍លក់ (Sales Report)":
    st.title("📊 របាយការណ៍លក់ (Sales Report)")
    if st.session_state.sales_history:
        st.dataframe(pd.DataFrame(st.session_state.sales_history))
    else:
        st.info("មិនទាន់មានប្រវត្តិលក់នៅឡើយទេ!")
