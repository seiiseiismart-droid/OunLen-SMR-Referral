import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Professional POS & Sales Report",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------------
# 2. Control Panel សម្រាប់កែប្រែ Style ប៊ូតុង និង តួអក្សរ (Sidebar Settings)
# ----------------------------------------------------------------
st.sidebar.header("🎨 កែសម្រួល Style ប្រព័ន្ធ (Styling Settings)")

# កំណត់ Default Values ក្នុង Session State
if "btn_bg_color" not in st.session_state:
    st.session_state.btn_bg_color = "#e11d48"  # ពណ៌ប៊ូតុង Primary (ក្រហមឈាមជ្រូក)
if "btn_text_color" not in st.session_state:
    st.session_state.btn_text_color = "#ffffff"  # ពណ៌អក្សរលើប៊ូតុង
if "btn_font_size" not in st.session_state:
    st.session_state.btn_font_size = 15  # ទំហំអក្សរ (px)
if "btn_border_radius" not in st.session_state:
    st.session_state.btn_border_radius = 10  # កោងជ្រុងប៊ូតុង (px)
if "btn_height" not in st.session_state:
    st.session_state.btn_height = 42  # កម្ពស់ប៊ូតុង (px)

# ឧបករណ៍កែប្រែក្នុង Sidebar
st.sidebar.subheader("🔘 កែសម្រួល ប៊ូតុង (Button Controls)")
btn_bg = st.sidebar.color_picker("ពណ៌ background ប៊ូតុង (Primary)", st.session_state.btn_bg_color)
btn_text = st.sidebar.color_picker("ពណ៌តួអក្សរលើប៊ូតុង", st.session_state.btn_text_color)
btn_size = st.sidebar.slider("ទំហំតួអក្សរលើប៊ូតុង (Font Size)", 10, 24, st.session_state.btn_font_size)
btn_radius = st.sidebar.slider("កម្រិតកោងជ្រុងប៊ូតុង (Border Radius)", 0, 30, st.session_state.btn_border_radius)
btn_h = st.sidebar.slider("កម្ពស់ប៊ូតុង (Button Height)", 30, 60, st.session_state.btn_height)

# Dynamic CSS Injecting
st.markdown(f"""
<style>
    /* ទម្រង់ Font & Background រួមនៃ App */
    .stApp {{
        background-color: #fff1f2 !important;
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif !important;
        color: #0f172a !important;
    }}

    h1, h2, h3, h4, h5, h6, p, label, div, span {{
        color: #0f172a !important;
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif !important;
    }}

    /* ------------------------------------ */
    /* កំណត់ Style លើប៊ូតុងទាំងអស់ក្នុងប្រព័ន្ធ (Button Styling) */
    /* ------------------------------------ */
    .stButton > button {{
        border-radius: {btn_radius}px !important;
        font-size: {btn_size}px !important;
        font-weight: 800 !important;
        min-height: {btn_h}px !important;
        transition: all 0.2s ease-in-out !important;
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif !important;
    }}

    /* ប៊ូតុងប្រភេទ Primary (ដូចជា Pay, Accept, Confirm...) */
    button[kind="primary"] {{
        background: {btn_bg} !important;
        color: {btn_text} !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
    }}

    /* ប៊ូតុងប្រភេទ Secondary */
    button[kind="secondary"] {{
        background-color: #ffffff !important;
        color: {btn_bg} !important;
        border: 2px solid {btn_bg} !important;
    }}

    /* Product Card CSS */
    .product-card {{
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
    }}
    .product-card:hover {{ border-color: {btn_bg}; }}
    .product-icon {{ font-size: 36px; margin: 4px 0; }}
    .product-title {{ font-size: 14px; font-weight: 900; height: 38px; overflow: hidden; line-height: 1.3; }}
    .product-code {{ font-size: 11px; color: #be123c !important; font-weight: 800; }}
    .product-price {{ font-size: 16px; font-weight: 900; color: #047857 !important; margin: 4px 0; }}

    /* Layout នៃ Cart */
    .cart-container {{
        background: #ffffff;
        border: 2px solid #f472b6;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 3. Data Initialization
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
# 4. Helper Functions
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
                background-color: {btn_bg}; color: {btn_text}; border: none;
                padding: 12px; font-size: {btn_size}px; font-weight: bold;
                border-radius: {btn_radius}px; cursor: pointer; width: 100%; margin-bottom: 10px;
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
# 5. Dialogs (Pop-ups)
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

# Open dialogs based on session state
if st.session_state.get("show_payment_dialog", False):
    payment_dialog()

if st.session_state.get("show_receipt_dialog", False):
    receipt_dialog()

# ----------------------------------------------------------------
# 6. Main Navigation Menu
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
        if c_col2.button("👤+", key="btn_quick_cust", type="secondary"):
            st.toast("បញ្ចូលឈ្មោះអតិថិជនរួចរាល់")

        # Cart Items Header & Table
        st.markdown("""
        <div style="background-color: #fff1f2; padding: 8px 10px; border-radius: 8px; border: 1px solid #fda4af; font-size: 13px; font-weight: 800; margin: 8px 0; color: #9f1239;">
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
                ic1.markdown(f"<div style='font-size:13px; font-weight:800;'>{item['name']}</div>", unsafe_allow_html=True)
                ic2.markdown(f"<div style='font-size:13px; text-align:center;'>${item['price']:.2f}</div>", unsafe_allow_html=True)
                
                # Qty selector
                new_q = ic3.number_input("qty", min_value=1, value=int(item["qty"]), key=f"cart_q_{idx}", label_visibility="collapsed")
                if new_q != item["qty"]:
                    st.session_state.cart[idx]["qty"] = new_q
                    st.session_state.cart[idx]["total"] = new_q * item["price"]
                    st.rerun()

                ic4.markdown(f"<div style='font-size:13px; text-align:right; font-weight:800;'>${item['total']:.2f}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; padding:20px; color:#94a3b8; font-size:14px; font-weight:700;'>No products available in the list</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 10px 0; border-top: 1px dashed #f472b6;'>", unsafe_allow_html=True)

        # Total Calculations
        discount_val = (subtotal * st.session_state.discount_pct) / 100
        grand_total_usd = subtotal - discount_val
        grand_total_khr = round(grand_total_usd * EXCHANGE_RATE)

        st.markdown(f"""
        <div style="font-size: 15px; line-height: 1.8;">
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
            <div style="display:flex; justify-content:space-between; font-size:19px; font-weight:900; color:#0284c7;">
                <span>Grand Total:</span> <span>$ {grand_total_usd:.2f}</span>
            </div>
            <div style="display:flex; justify-content:flex-end; font-size:15px; font-weight:800; color:#059669;">
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
                if st.button(method, key=f"pay_meth_{m_idx}", type="primary" if st.session_state.payment_method == method else "secondary", use_container_width=True):
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
        st.markdown('<div class="btn-discount" style="margin-top: 8px;">', unsafe_allow_html=True)
        if st.button("🎁 កំណត់ Discount (%)", key="btn_open_disc", use_container_width=True):
            set_discount_dialog()
        st.markdown('</div>', unsafe_allow_html=True)

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

        if confirm_c2.button("❌ បោះបង់", type="secondary", use_container_width=True):
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
    st.markdown("## 📊 របាយការណ៍លក់ និង ទិន្នន័យចំណូល")
    
    if not st.session_state.sales_history:
        st.info("💡 មិនទាន់មានទិន្នន័យលក់នៅឡើយទេ។ សូមធ្វើការលក់នៅលើផ្ទាំង POS ជាមុនសិន।")
    else:
        filter_col1, _ = st.columns([2, 2])
        with filter_col1:
            today = datetime.now().date()
            # ជ្រើសរើសចន្លោះថ្ងៃខែឆ្នាំ (Date Range)
            date_range = st.date_input(
                "🗓️ ជ្រើសរើសចន្លោះកាលបរិច្ឆេទ (Filter Date Range):",
                value=(today, today)
            )

        # ឆែកមើលការជ្រើសរើសចន្លោះថ្ងៃ (Start Date & End Date)
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        elif isinstance(date_range, tuple) and len(date_range) == 1:
            start_date = end_date = date_range[0]
        else:
            start_date = end_date = date_range

        sales_data = []
        total_sales_usd = 0.0
        total_sales_khr = 0
        total_transactions = 0

        for sale in st.session_state.sales_history:
            # បំបែកយកតែថ្ងៃខែឆ្នាំ YYYY-MM-DD
            sale_date = datetime.strptime(sale.get("date", "").split(" ")[0], "%Y-%m-%d").date()
            
            # ត្រួតពិនិត្យថា តើថ្ងៃលក់ស្ថិតនៅក្នុងចន្លោះថ្ងៃដែលបានជ្រើសរើសឬទេ
            if start_date <= sale_date <= end_date:
                total_val = sale.get("grand_total_usd", sale.get("total_usd", 0.0))
                total_khr = sale.get("grand_total_khr", round(total_val * EXCHANGE_RATE))
                
                total_sales_usd += total_val
                total_sales_khr += total_khr
                total_transactions += 1
                
                sales_data.append({
                    "Invoice No": sale.get("inv_no"),
                    "Date": sale.get("date", "").split(" ")[0],
                    "Time": sale.get("date", "").split(" ")[-1],
                    "Customer": sale.get("customer"),
                    "Subtotal ($)": f"${sale.get('subtotal', 0.0):.2f}",
                    "Discount ($)": f"-${sale.get('discount', 0.0):.2f}",
                    "Grand Total ($)": f"${total_val:.2f}",
                    "Grand Total (៛)": f"៛ {total_khr:,}"
                })

        # បង្ហាញ Key Metrics
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("📦 ការលក់សរុប (Transactions)", f"{total_transactions} លើក")
        m_col2.metric("💵 ចំណូលសរុប ($)", f"${total_sales_usd:.2f}")
        m_col3.metric("៛ ចំណូលសរុប (៛)", f"៛ {total_sales_khr:,}")

        st.markdown("---")
        
        # បង្ហាញចំណងជើងចន្លោះថ្ងៃ
        if start_date == end_date:
            date_str_display = f"{start_date}"
        else:
            date_str_display = f"{start_date} ដល់ {end_date}"
            
        st.markdown(f"### 📋 បញ្ជីវិក្កយបត្រ ({date_str_display})")
        
        if sales_data:
            st.dataframe(pd.DataFrame(sales_data), use_container_width=True, hide_index=True)
        else:
            st.warning(f"ពុំមានទិន្នន័យលក់សម្រាប់ចន្លោះថ្ងៃទី {date_str_display} ទេ។")
