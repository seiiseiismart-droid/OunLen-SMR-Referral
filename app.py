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

# Custom High-Contrast CSS
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #fdf2f8 !important;
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif;
        color: #0f172a !important;
    }

    /* Force button styles across Streamlit elements */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        transition: all 0.2s ease-in-out !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* Category Left Sidebar Buttons */
    div[data-testid="column"]:nth-child(1) div.stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #831843 !important;
        border: 2px solid #f472b6 !important;
        font-size: 15px !important;
        padding: 8px 12px !important;
    }
    div[data-testid="column"]:nth-child(1) div.stButton > button[kind="secondary"]:hover {
        background-color: #fce7f3 !important;
        color: #be185d !important;
        border-color: #db2777 !important;
    }
    div[data-testid="column"]:nth-child(1) div.stButton > button[kind="primary"] {
        background-color: #e11d48 !important;
        color: #ffffff !important;
        border: 2px solid #be123c !important;
        font-size: 16px !important;
        font-weight: 800 !important;
    }

    /* Service / Product Card Styling */
    .product-card {
        background: #ffffff;
        border: 2px solid #f472b6;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-icon { font-size: 38px; margin: 4px 0; }
    .product-title { font-size: 14px; font-weight: 700; color: #0f172a !important; height: 38px; overflow: hidden; }
    .product-code { font-size: 11px; color: #be123c !important; font-weight: 700; }
    .product-price { font-size: 16px; font-weight: 800; color: #047857 !important; margin: 4px 0; }

    /* "➕ បញ្ចូល Cart" Buttons under Services */
    .add-cart-btn div.stButton > button {
        background-color: #db2777 !important;
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        border: none !important;
        width: 100% !important;
        height: 38px !important;
        box-shadow: 0 2px 4px rgba(219, 39, 119, 0.3) !important;
    }
    .add-cart-btn div.stButton > button:hover {
        background-color: #be185d !important;
        color: #ffffff !important;
    }

    /* Cart Right Panel Styling */
    .cart-container {
        background: #ffffff;
        border: 2px solid #f472b6;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    /* Payment Methods Buttons (Cash, Paystack, Razorpay, etc.) */
    div[data-testid="column"]:nth-child(3) div.stButton > button[kind="secondary"] {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        border: 2px solid #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }
    div[data-testid="column"]:nth-child(3) div.stButton > button[kind="primary"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border: 2px solid #0369a1 !important;
        font-size: 14px !important;
        font-weight: 800 !important;
    }

    /* Action Buttons (Cancel / Draft / Save & Complete) */
    .btn-cancel div.stButton > button {
        background-color: #f87171 !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 800 !important;
        border: 2px solid #dc2626 !important;
        height: 48px !important;
    }
    .btn-cancel div.stButton > button:hover {
        background-color: #dc2626 !important;
    }

    .btn-draft div.stButton > button {
        background-color: #facc15 !important;
        color: #713f12 !important;
        font-size: 15px !important;
        font-weight: 800 !important;
        border: 2px solid #eab308 !important;
        height: 48px !important;
    }
    .btn-draft div.stButton > button:hover {
        background-color: #eab308 !important;
    }

    .btn-pay div.stButton > button {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        border: 2px solid #0369a1 !important;
        height: 48px !important;
    }
    .btn-pay div.stButton > button:hover {
        background-color: #0369a1 !important;
    }

    /* Discount Button Style */
    .btn-disc div.stButton > button {
        background-color: #8b5cf6 !important;
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        border: 2px solid #7c3aed !important;
    }
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
if "discount_pct" not in st.session_state:
    st.session_state.discount_pct = 0.0
if "hold_list" not in st.session_state:
    st.session_state.hold_list = []
if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None
if "show_payment_modal" not in st.session_state:
    st.session_state.show_payment_modal = False
if "payment_method" not in st.session_state:
    st.session_state.payment_method = "Cash"

# ----------------------------------------------------------------
# 3. Helper Functions
# ----------------------------------------------------------------
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
# 4. Main Navigation Menu
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
    
    col_cat, col_prod, col_cart = st.columns([1.2, 3.2, 2.4], gap="small")

    # ================= 1. LEFT PANEL: Categories =================
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

    # ================= 2. CENTER PANEL: Services Grid =================
    with col_prod:
        st.markdown("##### 💇‍♀️ សេវាកម្ម (Services)")
        
        search_query = st.text_input("Search / Scan Code", placeholder="[|||] ស្វែងរកតាមកូដ ឬ ឈ្មោះសេវាកម្ម...", label_visibility="collapsed")
        
        if st.session_state.selected_category == "ទាំងអស់ (All)":
            filtered_services = st.session_state.services_catalog
        else:
            filtered_services = [s for s in st.session_state.services_catalog if s["category"] == st.session_state.selected_category]

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

    # ================= 3. RIGHT PANEL: Order Cart =================
    with col_cart:
        st.markdown("<div class='cart-container'>", unsafe_allow_html=True)
        
        c_col1, c_col2 = st.columns([4, 1])
        c_name = c_col1.text_input("Customer Name", value=st.session_state.customer_name, label_visibility="collapsed", placeholder="Enter Customer name or phone number")
        st.session_state.customer_name = c_name
        if c_col2.button("👤+", key="btn_quick_cust"):
            st.toast("បញ្ចូលឈ្មោះអតិថិជនរួចរាល់")

        st.markdown("""
        <div style="background-color: #f8fafc; padding: 6px 10px; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 12px; font-weight: bold; margin: 8px 0;">
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
                
                new_q = ic3.number_input("qty", min_value=1, value=int(item["qty"]), key=f"cart_q_{idx}", label_visibility="collapsed")
                if new_q != item["qty"]:
                    st.session_state.cart[idx]["qty"] = new_q
                    st.session_state.cart[idx]["total"] = new_q * item["price"]
                    st.rerun()

                ic4.markdown(f"<div style='font-size:12px; text-align:right; font-weight:bold;'>${item['total']:.2f}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; padding:20px; color:#64748b; font-size:13px; font-weight:bold;'>No products available in the list</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 10px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)

        discount_val = (subtotal * st.session_state.discount_pct) / 100
        grand_total_usd = subtotal - discount_val
        grand_total_khr = round(grand_total_usd * EXCHANGE_RATE)

        st.markdown(f"""
        <div style="font-size: 13px; line-height: 1.8;">
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
            <div style="display:flex; justify-content:space-between; font-size:16px; font-weight:bold; color:#0284c7;">
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
                if st.button(method, key=f"pay_meth_{m_idx}", type="primary" if st.session_state.payment_method == method else "secondary", use_container_width=True):
                    st.session_state.payment_method = method
                    st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Action Buttons (Cancel / Draft / Save & Complete)
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

        st.markdown('<div class="btn-disc">', unsafe_allow_html=True)
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
            st.success("🎉 ការទូទាត់ប្រាក់បានជោគជ័យ!")
            st.rerun()

        if confirm_c2.button("❌ បោះបង់", use_container_width=True):
            st.session_state.show_payment_modal = False
            st.rerun()
