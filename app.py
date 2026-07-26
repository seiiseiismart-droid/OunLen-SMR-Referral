import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------------------------------------------------------
# 1. Page Config
# ----------------------------------------------------------------
st.set_page_config(
    page_title="Ready POS System",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------------------
# 2. Custom CSS for Ready POS UI
# ----------------------------------------------------------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #f0f4f9 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Top Navigation Header */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #ffffff;
        padding: 10px 20px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 10px;
    }
    .brand-logo {
        font-size: 24px;
        font-weight: 800;
        color: #0284c7;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .header-time {
        font-size: 16px;
        font-weight: 600;
        color: #334155;
    }

    /* Product Cards Grid */
    .product-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.1s ease-in-out;
    }
    .product-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }
    .product-img {
        width: 100%;
        height: 100px;
        object-fit: contain;
        border-radius: 6px;
        margin-bottom: 6px;
    }
    .product-title {
        font-size: 13px;
        font-weight: 700;
        color: #0f172a;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .product-code {
        font-size: 10px;
        color: #94a3b8;
    }
    .product-stock {
        font-size: 11px;
        font-weight: 600;
        color: #0284c7;
    }

    /* Cart Table Header */
    .cart-header-box {
        background-color: #bae6fd;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 700;
        color: #0369a1;
        display: flex;
        justify-content: space-between;
    }

    /* Summary Section Right Side */
    .summary-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 15px;
        font-size: 13px;
        line-height: 2;
    }
    .summary-row {
        display: flex;
        justify-content: space-between;
        color: #334155;
    }
    .summary-total {
        font-size: 18px;
        font-weight: bold;
        color: #0284c7;
        border-top: 1px dashed #cbd5e1;
        padding-top: 5px;
        margin-top: 5px;
    }

    /* Action Buttons */
    .btn-cancel div.stButton > button {
        background-color: #ffe4e6 !important;
        color: #e11d48 !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    .btn-draft div.stButton > button {
        background-color: #fef08a !important;
        color: #ca8a04 !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    .btn-save div.stButton > button {
        background-color: #38bdf8 !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 3. Session States & Sample Data
# ----------------------------------------------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"
if "selected_payment" not in st.session_state:
    st.session_state.selected_payment = "Cash"

# Products Database
products_db = [
    {"code": "EDLJKSSY", "name": "Advanced air purifier", "price": 45.0, "stock": 167, "category": "Electronics", "img": "https://picsum.photos/id/1060/200/200"},
    {"code": "SWr7NeSg", "name": "Smart LED Light With Rem..", "price": 12.0, "stock": 164, "category": "Electronics", "img": "https://picsum.photos/id/1059/200/200"},
    {"code": "HBf1qDvIv3", "name": "88 In 1 Automotive Test L..", "price": 28.5, "stock": 179, "category": "Gadgets", "img": "https://picsum.photos/id/1010/200/200"},
    {"code": "rTTuVyp7", "name": "Smart USBC Multiplug", "price": 15.0, "stock": 130, "category": "Electronics", "img": "https://picsum.photos/id/1062/200/200"},
    {"code": "uSKiDHd0", "name": "Bluetooth Wireless Mini P..", "price": 18.0, "stock": 80, "category": "Gadgets", "img": "https://picsum.photos/id/1082/200/200"},
    {"code": "btpxWMY5", "name": "Skullcandy Smokin Buds I..", "price": 25.0, "stock": 180, "category": "Gadgets", "img": "https://picsum.photos/id/1025/200/200"},
    {"code": "NwEriqwZ4", "name": "Apple AirPods Pro (2nd G..", "price": 199.0, "stock": 184, "category": "Apple", "img": "https://picsum.photos/id/1005/200/200"},
    {"code": "GgouxvwW", "name": "TAURI iPhone 13 Protecti..", "price": 10.0, "stock": 195, "category": "Apple", "img": "https://picsum.photos/id/1011/200/200"},
    {"code": "YwWiWmSc", "name": "Iuyhou Four Season Skinny", "price": 22.0, "stock": 199, "category": "Cloth", "img": "https://picsum.photos/id/1027/200/200"},
    {"code": "gtFI7RkT", "name": "Long Halter V Neck Velvet..", "price": 35.0, "stock": 197, "category": "Cloth", "img": "https://picsum.photos/id/1022/200/200"},
]

categories = [
    {"name": "Food", "img": "https://picsum.photos/id/1080/80/80"},
    {"name": "Electronics", "img": "https://picsum.photos/id/1060/80/80"},
    {"name": "Cloth", "img": "https://picsum.photos/id/1027/80/80"},
    {"name": "Gadgets", "img": "https://picsum.photos/id/1025/80/80"},
    {"name": "Home Appliances", "img": "https://picsum.photos/id/1068/80/80"},
    {"name": "Apple", "img": "https://picsum.photos/id/1005/80/80"},
    {"name": "Samsung", "img": "https://picsum.photos/id/1010/80/80"},
]

# ----------------------------------------------------------------
# 4. Top Header
# ----------------------------------------------------------------
curr_time = datetime.now().strftime("%d %b, %Y | %H:%M")
st.markdown(f"""
<div class="top-header">
    <div class="brand-logo">🛒 Ready POS <span style="font-size: 11px; color: #64748b; font-weight: normal;">Powering Your Business</span></div>
    <div class="header-time">{curr_time} 🏠 📋 ⛶ 🚪</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 5. Main Layout Split (3 Columns)
# ----------------------------------------------------------------
col_cat, col_prod, col_cart = st.columns([1, 2.8, 2.2], gap="small")

# ================================================================
# LEFT COLUMN: CATEGORIES & BRANDS
# ================================================================
with col_cat:
    tab_cat, tab_brand = st.tabs(["Categories", "Brands"])
    
    with tab_cat:
        if st.button("🌐 All Categories", use_container_width=True):
            st.session_state.selected_category = "All"
            st.rerun()
            
        for c in categories:
            c_col1, c_col2 = st.columns([1, 2])
            with c_col1:
                st.image(c["img"], width=50)
            with c_col2:
                if st.button(c["name"], key=f"cat_{c['name']}", use_container_width=True):
                    st.session_state.selected_category = c["name"]
                    st.rerun()

    with tab_brand:
        st.caption("Brand Filter")
        st.button("Apple", use_container_width=True)
        st.button("Samsung", use_container_width=True)

# ================================================================
# MIDDLE COLUMN: PRODUCTS GRID & SEARCH
# ================================================================
with col_prod:
    st.markdown("<h4 style='text-align: center; color: #0284c7; margin:0;'>Products</h4>", unsafe_allow_html=True)
    
    # Search Input Bar
    search_q = st.text_input("Search", placeholder="Scan/Search featured product by name or code...", label_visibility="collapsed")

    # Filter Products
    filtered_prods = products_db
    if st.session_state.selected_category != "All":
        filtered_prods = [p for p in filtered_prods if p["category"] == st.session_state.selected_category]
    if search_q.strip():
        filtered_prods = [p for p in filtered_prods if search_q.lower() in p["name"].lower() or search_q.lower() in p["code"].lower()]

    # Render Product Cards Grid (4 Columns)
    grid_cols = st.columns(4)
    for idx, p in enumerate(filtered_prods):
        with grid_cols[idx % 4]:
            st.markdown(f"""
            <div class="product-card">
                <img src="{p['img']}" class="product-img">
                <div class="product-title">{p['name']}</div>
                <div class="product-code">{p['code']}</div>
                <div class="product-stock">In Stock: {p['stock']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"+ ${p['price']:.2f}", key=f"add_{p['code']}", use_container_width=True):
                # Add to Cart Logic
                existing = next((item for item in st.session_state.cart if item["code"] == p["code"]), None)
                if existing:
                    existing["qty"] += 1
                else:
                    st.session_state.cart.append({
                        "code": p["code"],
                        "name": p["name"],
                        "price": p["price"],
                        "qty": 1,
                        "tax": 0.0
                    })
                st.rerun()

# ================================================================
# RIGHT COLUMN: CART, CUSTOMER & PAYMENT
# ================================================================
with col_cart:
    # Customer Selection Line
    cust_col1, cust_col2 = st.columns([5, 1])
    with cust_col1:
        st.text_input("Customer", placeholder="👤 Enter Customer name or phone number", label_visibility="collapsed")
    with cust_col2:
        st.button("➕", key="add_cust")

    # Cart Table Header
    st.markdown("""
    <div class="cart-header-box">
        <span style="width: 30%;">Product</span>
        <span style="width: 15%;">Variant</span>
        <span style="width: 15%;">Tax</span>
        <span style="width: 15%;">Price</span>
        <span style="width: 10%;">QTY</span>
        <span style="width: 15%; text-align: right;">Subtotal</span>
    </div>
    """, unsafe_allow_html=True)

    # Cart Items Display
    if not st.session_state.cart:
        st.markdown("<div style='text-align:center; padding: 20px; color:#94a3b8;'>No products available in the list</div>", unsafe_allow_html=True)
    else:
        for idx, item in enumerate(st.session_state.cart):
            r1, r2, r3, r4, r5, r6 = st.columns([2.5, 1, 1, 1, 1, 1.2])
            r1.caption(item["name"])
            r2.caption("-")
            r3.caption("$0.00")
            r4.caption(f"${item['price']:.2f}")
            
            # Qty update
            new_qty = r5.number_input("Q", min_value=1, value=item["qty"], key=f"qty_{idx}", label_visibility="collapsed")
            if new_qty != item["qty"]:
                st.session_state.cart[idx]["qty"] = new_qty
                st.rerun()
                
            subtot = item["price"] * item["qty"]
            r6.caption(f"${subtot:.2f}")

    # Summary Calculations
    total_qty = sum(item["qty"] for item in st.session_state.cart)
    total_amount = sum(item["price"] * item["qty"] for item in st.session_state.cart)
    discount = 0.0
    coupon = 0.0
    grand_total = total_amount - discount - coupon

    # Summary Box HTML
    st.markdown(f"""
    <div class="summary-box">
        <div class="summary-row"><span>Total Products:</span> <b>{len(st.session_state.cart)}({total_qty})</b></div>
        <div class="summary-row"><span>Total Amount:</span> <b>$ {total_amount:.2f}</b></div>
        <div class="summary-row"><span>Discount:</span> <b style="color:#f43f5e;">- $ {discount:.2f}</b></div>
        <div class="summary-row"><span>Coupon:</span> <b>$ {coupon:.2f}</b></div>
        <div class="summary-row summary-total"><span>Grand Total:</span> <span>$ {grand_total:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Payment Gateways Tabs / Buttons
    st.caption("Select Payment Method:")
    p_cols = st.columns(5)
    pay_methods = ["Cash", "Paystack", "Razorpay", "PayPal", "Stripe"]
    for i, pm in enumerate(pay_methods):
        with p_cols[i]:
            if st.button(pm, key=f"pay_{pm}", use_container_width=True):
                st.session_state.selected_payment = pm
                st.toast(f"Selected: {pm}")

    st.write("")

    # Bottom Action Buttons
    act_col1, act_col2, act_col3 = st.columns(3)
    
    with act_col1:
        st.markdown("<div class='btn-cancel'>", unsafe_allow_html=True)
        if st.button("Cancel", use_container_width=True):
            st.session_state.cart = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with act_col2:
        st.markdown("<div class='btn-draft'>", unsafe_allow_html=True)
        if st.button("Draft", use_container_width=True):
            st.toast("Saved to Draft!")
        st.markdown("</div>", unsafe_allow_html=True)

    with act_col3:
        st.markdown("<div class='btn-save'>", unsafe_allow_html=True)
        if st.button("Save & Complete", use_container_width=True):
            if st.session_state.cart:
                st.success("Transaction Completed Successfully!")
                st.session_state.cart = []
                st.rerun()
            else:
                st.warning("Cart is empty!")
        st.markdown("</div>", unsafe_allow_html=True)
