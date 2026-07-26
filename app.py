import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
from datetime import datetime

# ----------------------------------------------------------------
# 0. BACKEND DATABASE SETUP (SQLite)
# ----------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect('ounlen_pos.db', check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Table Services
    c.execute('''
        CREATE TABLE IF NOT EXISTS services (
            code TEXT PRIMARY KEY,
            category TEXT,
            name TEXT,
            price REAL,
            icon TEXT
        )
    ''')
    
    # 2. Table Customers
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            type TEXT
        )
    ''')

    # 3. Table Sales History
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            inv_no TEXT PRIMARY KEY,
            date_time TEXT,
            customer TEXT,
            payment_method TEXT,
            subtotal REAL,
            discount REAL,
            grand_total_usd REAL,
            grand_total_khr REAL,
            paid_usd REAL,
            paid_khr REAL,
            change_usd REAL,
            change_khr REAL
        )
    ''')

    # Insert default services if empty
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        default_services = [
            ("S01", "✨ សេវាកម្មទូទៅ", "ម៉ាសស្កាតបញ្ចូលវីតាមីនសារាយ", 15.0, "🌿"),
            ("S02", "✨ សេវាកម្មទូទៅ", "ម៉ាសស្កាតបញ្ចូលវីតាមីន baby Glow", 15.0, "✨"),
            ("S03", "✨ សេវាកម្មទូទៅ", "ម៉ាសស្កាតបញ្ចូលវីតាមីន college", 12.5, "💧"),
            ("S04", "✨ សេវាកម្មទូទៅ", "ញេចសម្អាតគ្រាប់មុន ជម្រុះកោសិកា", 7.5, "🧖‍♀️"),
            ("S05", "✨ សេវាកម្មទូទៅ", "ម៉ាសស្កាតបញ្ចូលវីតាមីនVIP ពីមុខ ដល់ ក", 25.0, "👑"),
            ("S06", "✨ សេវាកម្មទូទៅ", "កក់សក់ + បិទម៉ាស", 4.0, "💇‍♀️"),
            ("L01", "⚡ សេវាកម្ម Laser", "បាញ់ Laser ក្លៀក", 5.0, "⚡"),
            ("L02", "⚡ សេវាកម្ម Laser", "បាញ់ Laser រោមដៃ", 9.0, "⚡")
        ]
        c.executemany("INSERT INTO services VALUES (?, ?, ?, ?, ?)", default_services)

    conn.commit()
    conn.close()

init_db()

# DB Helper Functions
def load_services_from_db():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT code, category, name, price, icon FROM services", conn)
    conn.close()
    return df.to_dict('records')

def save_sale_to_db(data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['inv_no'], data['date'], data['customer'], data['payment_method'],
        data['subtotal'], data['discount'], data['grand_total_usd'], data['grand_total_khr'],
        data['paid_usd'], data['paid_khr'], data['change_usd'], data['change_khr']
    ))
    conn.commit()
    conn.close()

def load_sales_from_db():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM sales ORDER BY date_time DESC", conn)
    conn.close()
    return df

# ----------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Professional POS & Sales Report",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #fff1f2 !important; font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif; color: #0f172a !important; }
    h1, h2, h3, h4, h5, h6, p, label, div, span { color: #0f172a !important; }
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] > div { background-color: #ffffff !important; padding: 8px 14px !important; border-radius: 12px !important; border: 2px solid #f472b6 !important; }
    .product-card { background: #ffffff; border: 2px solid #fda4af; border-radius: 14px; padding: 12px; text-align: center; height: 100%; }
    .product-icon { font-size: 40px; }
    .product-title { font-size: 15px; font-weight: 900; color: #0f172a !important; }
    .product-price { font-size: 18px; font-weight: 900; color: #047857 !important; }
    .cart-container { background: #ffffff; border: 2px solid #f472b6; border-radius: 14px; padding: 16px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. Session States Initializing
# ----------------------------------------------------------------
EXCHANGE_RATE = 4100

if "categories" not in st.session_state:
    st.session_state.categories = ["✨ សេវាកម្មទូទៅ", "⚡ សេវាកម្ម Laser", "🧴 សេវាកម្ម ស្ប៉ា"]
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "ទាំងអស់ (All)"
if "customer_name" not in st.session_state:
    st.session_state.customer_name = "General Customer"
if "cart" not in st.session_state:
    st.session_state.cart = []
if "discount_pct" not in st.session_state:
    st.session_state.discount_pct = 0.0
if "payment_method" not in st.session_state:
    st.session_state.payment_method = "Cash"
if "show_payment_modal" not in st.session_state:
    st.session_state.show_payment_modal = False
if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None

# Always fetch fresh services from DB
st.session_state.services_catalog = load_services_from_db()

# ----------------------------------------------------------------
# 3. Helper Functions
# ----------------------------------------------------------------
def recalculate_item(item):
    base = item["price"] * item["qty"]
    disc_amount = (base * item["item_disc"]) / 100.0
    item["total"] = base - disc_amount

def add_to_cart(item):
    existing = next((i for i in st.session_state.cart if i["code"] == item["code"]), None)
    if existing:
        existing["qty"] += 1
        recalculate_item(existing)
    else:
        new_cart_item = {
            "code": item["code"],
            "name": item["name"],
            "price": item["price"],
            "qty": 1,
            "item_disc": 0.0,
            "total": item["price"]
        }
        st.session_state.cart.append(new_cart_item)

def reset_pos():
    st.session_state.cart = []
    st.session_state.discount_pct = 0.0
    st.session_state.customer_name = "General Customer"
    st.session_state.show_payment_modal = False

def generate_receipt_html(data):
    items_html = ""
    for item in data.get('items', []):
        disc_text = f" (-{item.get('item_disc', 0)}%)" if item.get('item_disc', 0) > 0 else ""
        items_html += f"""
        <tr>
            <td style="text-align: left;">{item.get('name', '')}{disc_text}</td>
            <td style="text-align: center;">{item.get('qty', 1)}</td>
            <td style="text-align: right;">${item.get('price', 0.0):.2f}</td>
            <td style="text-align: right;">${item.get('total', 0.0):.2f}</td>
        </tr>
        """
    return f"""
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <style>
        body {{ font-family: monospace; width: 72mm; margin: 0 auto; font-size: 12px; }}
        .text-center {{ text-align: center; }}
        .dashed {{ border-top: 1px dashed #000; margin: 6px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        .flex {{ display: flex; justify-content: space-between; }}
        .btn {{ background: #e11d48; color: white; border: none; padding: 10px; width: 100%; cursor: pointer; }}
        @media print {{ .no-print {{ display: none; }} }}
    </style></head><body>
        <button class="btn no-print" onclick="window.print()">🖨️ ព្រីនវិក្កយបត្រ (80mm)</button>
        <div class="text-center"><h2>💇‍♀️ អូនឡែន សម្រស់</h2></div>
        <div class="dashed"></div>
        <div class="flex"><span>លេខវិក្កយបត្រ:</span><b>{data.get('inv_no')}</b></div>
        <div class="flex"><span>កាលបរិច្ឆេទ:</span><span>{data.get('date')}</span></div>
        <div class="dashed"></div>
        <table>{items_html}</table>
        <div class="dashed"></div>
        <div class="flex"><b>សរុបត្រូវបង់:</b><b>${data.get('grand_total_usd',0.0):.2f}</b></div>
    </body></html>
    """

# ----------------------------------------------------------------
# 4. Main Menu
# ----------------------------------------------------------------
main_mode = st.radio("Navigation", ["🖥️ ផ្ទាំងលក់ (POS)", "🛠️ គ្រប់គ្រងសេវាកម្ម", "📊 របាយការណ៍លក់ (Saved DB)"], horizontal=True)

if main_mode == "🖥️ ផ្ទាំងលក់ (POS)":
    col_cat, col_prod, col_cart = st.columns([1.2, 3.2, 2.6])
    
    with col_cat:
        st.markdown("##### 📂 ប្រភេទ")
        if st.button("🌸 ទាំងអស់", use_container_width=True):
            st.session_state.selected_category = "ទាំងអស់ (All)"
        for cat in st.session_state.categories:
            if st.button(cat, use_container_width=True):
                st.session_state.selected_category = cat

    with col_prod:
        st.markdown("##### 💇‍♀️ សេវាកម្ម")
        items = st.session_state.services_catalog
        if st.session_state.selected_category != "ទាំងអស់ (All)":
            items = [i for i in items if i["category"] == st.session_state.selected_category]
            
        cols = st.columns(3)
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                st.markdown(f"""<div class="product-card">
                    <div class="product-icon">{item['icon']}</div>
                    <div class="product-title">{item['name']}</div>
                    <div class="product-price">${item['price']:.2f}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("➕ បញ្ចូល", key=f"add_{item['code']}"):
                    add_to_cart(item)
                    st.rerun()

    with col_cart:
        st.markdown("<div class='cart-container'>", unsafe_allow_html=True)
        st.markdown("##### 🛒 បញ្ជីជ្រើសរើស")
        subtotal = 0.0
        for idx, item in enumerate(st.session_state.cart):
            subtotal += item["total"]
            st.write(f"**{item['name']}** - ${item['price']} x {item['qty']} = **${item['total']:.2f}**")
        
        st.markdown("---")
        grand_total = subtotal - (subtotal * st.session_state.discount_pct / 100)
        st.markdown(f"### សរុប: **${grand_total:.2f}** ({round(grand_total * EXCHANGE_RATE):,} ៛)")
        
        if st.button("✅ ទូទាត់ និង រក្សាទុក (Save to DB)", type="primary", use_container_width=True):
            if st.session_state.cart:
                inv_no = f"INV-{int(datetime.now().timestamp())}"
                receipt_data = {
                    "inv_no": inv_no,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "customer": st.session_state.customer_name,
                    "payment_method": st.session_state.payment_method,
                    "items": st.session_state.cart.copy(),
                    "subtotal": subtotal,
                    "discount": 0.0,
                    "grand_total_usd": grand_total,
                    "grand_total_khr": round(grand_total * EXCHANGE_RATE),
                    "paid_usd": grand_total,
                    "paid_khr": 0,
                    "change_usd": 0.0,
                    "change_khr": 0
                }
                save_sale_to_db(receipt_data)
                st.session_state.last_receipt = receipt_data
                reset_pos()
                st.success("បានរក្សាទុកក្នុង Database រួចរាល់!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

elif main_mode == "📊 របាយការណ៍លក់ (Saved DB)":
    st.markdown("## 📊 របាយការណ៍លក់ពី Database")
    df_sales = load_sales_from_db()
    if not df_sales.empty:
        st.dataframe(df_sales, use_container_width=True)
        st.metric("ចំណូលសរុប ($)", f"${df_sales['grand_total_usd'].sum():.2f}")
    else:
        st.info("មិនទាន់មានទិន្នន័យលក់នៅក្នុង Database ទេ!")
