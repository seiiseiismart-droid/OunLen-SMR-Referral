import streamlit as st
import pandas as pd
from datetime import datetime

# កំណត់ Exchange Rate
EXCHANGE_RATE = 4100

# -------------------------------------------------------------------
# 1. POPUP សម្រាប់ទូទាត់ប្រាក់ (PAYMENT DIALOG)
# -------------------------------------------------------------------
@st.dialog("💵 ផ្ទាំងទទួលប្រាក់ (Payment)", width="large")
def payment_dialog():
    total_usd = st.session_state.get("cart_total_usd", 0.0)
    total_khr = round(total_usd * EXCHANGE_RATE)

    st.write(f"### ប្រាក់ត្រូវទូទាត់សរុប: **${total_usd:,.2f}** ({total_khr:,.0f} ៛)")
    
    col1, col2 = st.columns(2)
    with col1:
        paid_usd = st.number_input("ប្រាក់ទទួលជា ដុល្លារ ($):", min_value=0.0, value=total_usd, step=1.0)
    with col2:
        paid_khr = st.number_input("ប្រាក់ទទួលជា រៀល (៛):", min_value=0, value=0, step=1000)

    # គណនាប្រាក់ទទួលបានសរុបគិតជា $
    total_paid_in_usd = paid_usd + (paid_khr / EXCHANGE_RATE)
    change_usd = total_paid_in_usd - total_usd
    change_khr = round(change_usd * EXCHANGE_RATE)

    # បង្ហាញប្រាក់អាប់
    if change_usd >= 0:
        st.success(f"💰 **ប្រាក់អាប់:** ${change_usd:,.2f} / {change_khr:,.0f} ៛")
    else:
        st.error(f"⚠️ **នៅខ្វះ:** ${abs(change_usd):,.2f} / {abs(change_khr):,.0f} ៛")

    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("❌ បោះបង់", use_container_width=True):
        st.rerun()

    if c2.button("✅ បញ្ចប់ការទូទាត់", type="primary", use_container_width=True):
        if change_usd < 0:
            st.error("ប្រាក់ដែលទទួលបានមិនទាន់គ្រប់ចំនួនឡើយ!")
        else:
            # រក្សាទុកទិន្នន័យនៃការទូទាត់
            st.session_state.last_payment_info = {
                "paid_usd": paid_usd,
                "paid_khr": paid_khr,
                "change_usd": change_usd,
                "change_khr": change_khr
            }
            # រក្សាទុកក្នុងប្រវត្តិលក់ (Sales History)
            inv_number = f"INV-{len(st.session_state.get('sales_history', [])) + 1:04d}"
            sales_data = {
                "inv_no": inv_number,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "customer": st.session_state.get("selected_customer", "General Customer"),
                "items": st.session_state.get("cart", []),
                "grand_total_usd": total_usd
            }
            st.session_state.setdefault("sales_history", []).append(sales_data)
            st.session_state.last_invoice = sales_data
            
            # ផ្លាស់ប្តូរ State ដើម្បីបើកផ្ទាំងវិក្កយបត្រ
            st.session_state.show_payment_dialog = False
            st.session_state.show_receipt_dialog = True
            st.rerun()


# -------------------------------------------------------------------
# 2. POPUP សម្រាប់បង្ហាញវិក្កយបត្រ & Print (RECEIPT DIALOG)
# -------------------------------------------------------------------
@st.dialog("🧾 វិក្កយបត្រ (Receipt)", width="large")
def receipt_dialog():
    inv = st.session_state.get("last_invoice", {})
    pay = st.session_state.get("last_payment_info", {})

    st.markdown(f"### 🏪 ហាងកែសម្ផស្ស (Beauty Salon)")
    st.write(f"**លេខវិក្កយបត្រ:** {inv.get('inv_no')} | **កាលបរិច្ឆេទ:** {inv.get('date')}")
    st.write(f"**អតិថិជន:** {inv.get('customer')}")
    st.markdown("---")

    # តារាងទំនិញ
    items = inv.get("items", [])
    if items:
        df = pd.DataFrame(items)[["name", "price", "qty", "total"]]
        df.columns = ["សេវាកម្ម", "តម្លៃ ($)", "ចំនួន", "សរុប ($)"]
        st.table(df)

    total_usd = inv.get("grand_total_usd", 0.0)
    st.markdown(f"**សរុបត្រូវបង់:** ${total_usd:,.2f} ({round(total_usd * EXCHANGE_RATE):,.0f} ៛)")
    st.write(f"**ប្រាក់ទទួលបាន:** ${pay.get('paid_usd', 0):,.2f} + {pay.get('paid_khr', 0):,.0f} ៛")
    st.write(f"**ប្រាក់អាប់:** ${pay.get('change_usd', 0):,.2f} ({pay.get('change_khr', 0):,.0f} ៛)")

    st.markdown("---")
    
    col_print, col_close = st.columns(2)
    
    # ប៊ូតុង ព្រីន (Print Receipt)
    with col_print:
        # ប្រើ JavaScript សម្រាប់បញ្ជាឲ្យ Print ផ្ទាំង Receipt
        st.components.v1.html(
            """
            <button onclick="window.print()" style="
                width: 100%;
                background-color: #FF4B4B;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;">
                🖨️ ព្រីនវិក្កយបត្រ (Print)
            </button>
            """,
            height=50
        )

    with col_close:
        if st.button("✅ រួចរាល់ (បិទ)", use_container_width=True):
            # សម្អាត Cart ដើមី្បចាប់ផ្តើមលក់ថ្មី
            st.session_state.cart = []
            st.session_state.show_receipt_dialog = False
            st.rerun()


# -------------------------------------------------------------------
# 3. ការហៅប្រើប្រាស់ dialog តាម State
# -------------------------------------------------------------------
if st.session_state.get("show_payment_dialog", False):
    payment_dialog()

if st.session_state.get("show_receipt_dialog", False):
    receipt_dialog()

# -------------------------------------------------------------------
# 4. ផ្នែកចុចប៊ូតុង Payment លើអេក្រង់ POS (ឧទាហរណ៍ Cash, ABA...)
# -------------------------------------------------------------------
# កន្លែងចុចប៊ូតុង Cash / ABA / KHQR លើ POS UI របស់អ្នក៖
# if st.button("Cash", type="primary"):
#     st.session_state.cart_total_usd = 50.0 # តម្លៃសរុបចេញពី Cart របស់អ្នក
#     st.session_state.show_payment_dialog = True
#     st.rerun()import streamlit as st
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

    /* POS Action Buttons */
    .btn-cancel button {
        background-color: #dc2626 !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        height: 48px !important;
    }
    .btn-draft button {
        background-color: #d97706 !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        height: 48px !important;
    }
    .btn-pay button {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 17px !important;
        height: 48px !important;
    }
    .btn-discount button {
        background-color: #7c3aed !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 15px !important;
        height: 44px !important;
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
if "show_payment_modal" not in st.session_state:
    st.session_state.show_payment_modal = False
if "show_receipt_dialog" not in st.session_state:
    st.session_state.show_receipt_dialog = False
if "current_receipt" not in st.session_state:
    st.session_state.current_receipt = None
if "payment_method" not in st.session_state:
    st.session_state.payment_method = "Cash"

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
    st.session_state.show_payment_modal = False
    st.session_state.show_receipt_dialog = False

def generate_receipt_html(data):
    items_html = ""
    for item in data.get('items', []):
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
                background-color: #e11d48; color: white; border: none;
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
            <div class="flex-between"><span>លេខវិក្កយបត្រ:</span> <b>{data.get('inv_no', 'N/A')}</b></div>
            <div class="flex-between"><span>កាលបរិច្ឆេទ:</span> <span>{data.get('date', '')}</span></div>
            <div class="flex-between"><span>អតិថិជន:</span> <span>{data.get('customer', 'General')}</span></div>
            <div class="flex-between"><span>វិធីសាស្ត្រទូទាត់:</span> <span>{data.get('payment_method', 'Cash')}</span></div>
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
            <div class="flex-between"><span>សរុបរង (Subtotal):</span> <span>${data.get('subtotal', 0.0):.2f}</span></div>
            <div class="flex-between"><span>បញ្ចុះតម្លៃបន្ថែម:</span> <span>-${data.get('discount', 0.0):.2f}</span></div>
            <div class="dashed-line"></div>
            <div class="flex-between" style="font-size: 13px; font-weight: bold;">
                <span>ត្រូវបង់សរុប:</span> <span>${data.get('grand_total_usd', 0.0):.2f}</span>
            </div>
            <div class="flex-between" style="font-weight: bold;">
                <span>ជាប្រាក់រៀល:</span> <span>៛ {data.get('grand_total_khr', 0):,}</span>
            </div>
        </div>
        <div class="dashed-line"></div>
        <div style="font-size: 10px;">
            <div class="flex-between"><span>ប្រាក់ទទួលបាន ($):</span> <span>${data.get('paid_usd', 0.0):.2f}</span></div>
            <div class="flex-between"><span>ប្រាក់អាប់ ($):</span> <span>${data.get('change_usd', 0.0):.2f}</span></div>
            <div class="flex-between"><span>ប្រាក់អាប់ (៛):</span> <span>៛ {data.get('change_khr', 0):,}</span></div>
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

@st.dialog("🧾 វិក្កយបត្រទូទាត់ប្រាក់ (Receipt Preview)", width="large")
def show_receipt_modal_dialog():
    st.success("🎉 ការទូទាត់ប្រាក់ជោគជ័យ! លោកអ្នកអាចព្រីនវិក្កយបត្រខាងក្រោមបាន។")
    if st.session_state.current_receipt:
        html_code = generate_receipt_html(st.session_state.current_receipt)
        components.html(html_code, height=450, scrolling=True)
    
    if st.button("✅ រួចរាល់ / បញ្ចប់ប្រតិបត្តិការ (Reset POS)", type="primary", use_container_width=True):
        reset_pos()
        st.rerun()

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
        
        # Customer Select & Add VIP Customer
        c_col1, c_col2 = st.columns([4, 1])
        cust_names = [c["name"] for c in st.session_state.customers_list]
        selected_c = c_col1.selectbox("ជ្រើសរើសអតិថិជន", cust_names, index=cust_names.index(st.session_state.selected_customer) if st.session_state.selected_customer in cust_names else 0, label_visibility="collapsed")
        st.session_state.selected_customer = selected_c
        
        if c_col2.button("👤+", key="btn_quick_cust", type="secondary"):
            register_customer_dialog()

        # Cart Table Header
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
                
                # Interactive Qty
                new_q = ic2.number_input("qty", min_value=1, value=int(item["qty"]), key=f"cq_{idx}", label_visibility="collapsed")
                # Interactive Item Discount
                new_d = ic3.number_input("disc", min_value=0.0, max_value=100.0, value=float(item.get("item_disc", 0.0)), step=5.0, key=f"cd_{idx}", label_visibility="collapsed")
                
                if new_q != item["qty"] or new_d != item.get("item_disc", 0.0):
                    st.session_state.cart[idx]["qty"] = new_q
                    st.session_state.cart[idx]["item_disc"] = new_d
                    recalculate_item(st.session_state.cart[idx])
                    st.rerun()

                subtotal += item["total"]
                total_items_count += item["qty"]
                ic4.markdown(f"<div style='font-size:13px; text-align:right; font-weight:900;'>${item['total']:.2f}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; padding:20px; color:#94a3b8; font-size:13px; font-weight:700;'>មិនទាន់មានសេវាកម្មក្នុង Cart</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 8px 0; border-top: 1px dashed #f472b6;'>", unsafe_allow_html=True)

        # Global Discount & Grand Total
        global_discount_val = (subtotal * st.session_state.discount_pct) / 100.0
        grand_total_usd = subtotal - global_discount_val
        grand_total_khr = round(grand_total_usd * EXCHANGE_RATE)

        st.markdown(f"""
        <div style="font-size: 14px; line-height: 1.6;">
            <div style="display:flex; justify-content:space-between;">
                <span>ចំនួនសរុប (Total Items):</span> <b>{len(st.session_state.cart)} ({total_items_count})</b>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>តម្លៃសរុប (Subtotal):</span> <b>$ {subtotal:.2f}</b>
            </div>
            <div style="display:flex; justify-content:space-between; color:#dc2626;">
                <span>បញ្ចុះតម្លៃបន្ថែម ({st.session_state.discount_pct}%):</span> <b>-$ {global_discount_val:.2f}</b>
            </div>
            <hr style="margin:4px 0;">
            <div style="display:flex; justify-content:space-between; font-size:18px; font-weight:900; color:#0284c7;">
                <span>ត្រូវបង់សរុប:</span> <span>$ {grand_total_usd:.2f}</span>
            </div>
            <div style="display:flex; justify-content:flex-end; font-size:14px; font-weight:800; color:#059669;">
                <span>៛ {grand_total_khr:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)

        # Payment Methods
        p_cols = st.columns(4)
        methods = ["Cash", "ABA/KHQR", "Paystack", "Stripe"]
        for m_idx, method in enumerate(methods):
            with p_cols[m_idx]:
                if st.button(method, key=f"pay_meth_{m_idx}", type="primary" if st.session_state.payment_method == method else "secondary", use_container_width=True):
                    st.session_state.payment_method = method
                    st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Actions
        ac1, ac2, ac3 = st.columns([1, 1, 1.5])
        with ac1:
            st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
            if st.button("Cancel", key="pos_cancel", use_container_width=True):
                reset_pos()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with ac2:
            st.markdown('<div class="btn-draft">', unsafe_allow_html=True)
            if st.button("Draft", key="pos_draft", use_container_width=True):
                if st.session_state.cart:
                    st.toast("បានរក្សាទុក Draft!")
                    reset_pos()
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with ac3:
            st.markdown('<div class="btn-pay">', unsafe_allow_html=True)
            if st.button("Save & Complete", key="pos_pay", use_container_width=True):
                if not st.session_state.cart:
                    st.warning("សូមជ្រើសរើសសេវាកម្មជាមុនសិន!")
                else:
                    st.session_state.show_payment_modal = True
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-discount" style="margin-top: 6px;">', unsafe_allow_html=True)
        if st.button("🎁 កំណត់ Discount បន្ថែម (%)", key="btn_open_disc", use_container_width=True):
            set_global_discount_dialog()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # 4. PAYMENT MODAL
    if st.session_state.get("show_payment_modal", False):
        st.markdown("---")
        st.markdown("### 💵 បង្អួចទូទាត់ប្រាក់ (Payment Modal)")
        p_col1, p_col2 = st.columns(2)
        paid_usd = p_col1.number_input("ប្រាក់ទទួលបាន ($)", min_value=0.0, value=float(grand_total_usd))
        paid_khr = p_col2.number_input("ប្រាក់ទទួលបាន (៛)", min_value=0, step=1000)
        
        tot_paid = paid_usd + (paid_khr / EXCHANGE_RATE)
        change_u = max(0.0, tot_paid - grand_total_usd)
        change_k = round(change_u * EXCHANGE_RATE)
        
        st.info(f"💵 ប្រាក់អាប់ (Change): **$ {change_u:.2f}** ({change_k:,.0f} ៛)")
        
        confirm_c1, confirm_c2 = st.columns(2)
        if confirm_c1.button("✅ យល់ព្រមទូទាត់ និង បង្ហាញវិក្កយបត្រ", type="primary", use_container_width=True):
            inv_no = f"INV-{len(st.session_state.sales_history) + 1001}"
            receipt_data = {
                "inv_no": inv_no,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "customer": st.session_state.selected_customer,
                "payment_method": st.session_state.payment_method,
                "items": st.session_state.cart.copy(),
                "subtotal": subtotal,
                "discount": global_discount_val,
                "grand_total_usd": grand_total_usd,
                "grand_total_khr": grand_total_khr,
                "paid_usd": paid_usd,
                "paid_khr": paid_khr,
                "change_usd": change_u,
                "change_khr": change_k
            }
            
            st.session_state.current_receipt = receipt_data
            st.session_state.sales_history.append(receipt_data)
            st.session_state.show_payment_modal = False
            
            # Open Receipt Dialog immediately
            show_receipt_modal_dialog()

        if confirm_c2.button("❌ បោះបង់", type="secondary", use_container_width=True):
            st.session_state.show_payment_modal = False
            st.rerun()

# ================================================================
# MODE 2: SERVICE MANAGEMENT
# ================================================================
elif main_mode == "🛠️ គ្រប់គ្រងសេវាកម្ម (Services)":
    st.markdown("## 🛠️ គ្រប់គ្រងសេវាកម្ម (Manage Services)")
    col_s_add, col_s_edit = st.columns(2, gap="large")
    
    with col_s_add:
        st.markdown("### ➕ បន្ថែមសេវាកម្មថ្មី")
        with st.form("add_service_form", clear_on_submit=True):
            s_code = st.text_input("កូដសេវាកម្ម (Service Code)")
            s_name = st.text_input("ឈ្មោះសេវាកម្ម (Service Name)")
            s_cat = st.selectbox("ជ្រើសរើសប្រភេទសេវាកម្ម", st.session_state.categories)
            s_price = st.number_input("តម្លៃ ($)", min_value=0.0, value=10.0, step=0.5)
            s_icon = st.text_input("រូបតំណាង (Emoji Icon)", value="✨")
            
            if st.form_submit_button("➕ បញ្ចូលសេវាកម្មថ្មី", type="primary"):
                if s_code.strip() and s_name.strip():
                    new_item = {"code": s_code.strip().upper(), "category": s_cat, "name": s_name.strip(), "price": float(s_price), "icon": s_icon.strip() if s_icon.strip() else "✨"}
                    st.session_state.services_catalog.append(new_item)
                    st.success("បានបន្ថែមសេវាកម្មថ្មីជោគជ័យ!")
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
                    if e_col1.form_submit_button("✏️ រក្សាទុក", type="primary"):
                        target_item["name"] = edit_name.strip()
                        target_item["price"] = float(edit_price)
                        st.success("បានកែប្រែសេវាកម្មរួចរាល់!")
                        st.rerun()
                        
                    if e_col2.form_submit_button("🗑️ លុបសេវាកម្ម"):
                        st.session_state.services_catalog = [item for item in st.session_state.services_catalog if item["code"] != selected_code]
                        st.success("បានលុបសេវាកម្មរួចរាល់!")
                        st.rerun()

# ================================================================
# MODE 3: CATEGORY MANAGEMENT
# ================================================================
elif main_mode == "⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម (Categories)":
    st.markdown("## ⚙️ គ្រប់គ្រងប្រភេទសេវាកម្ម")
    new_cat_name = st.text_input("ឈ្មោះប្រភេទសេវាកម្មថ្មី:")
    if st.button("➕ បន្ថែមប្រភេទ", type="primary"):
        if new_cat_name.strip() and new_cat_name not in st.session_state.categories:
            st.session_state.categories.append(new_cat_name.strip())
            st.success("បានបន្ថែមជោគជ័យ!")
            st.rerun()

# ================================================================
# MODE 4: RECEIPT VIEW
# ================================================================
elif main_mode == "🧾 វិក្កយបត្រ (Last Receipt)":
    st.markdown("## 🧾 ប្រវត្តិប្រតិបត្តិការ និង ការពិនិត្យវិក្កយបត្រ (80mm Thermal Paper)")
    if not st.session_state.sales_history:
        st.info("💡 មិនទាន់មានប្រវត្តិប្រតិបត្តិការ/ការលក់នៅឡើយទេ។")
    else:
        col_list, col_preview = st.columns([1.5, 1], gap="medium")
        with col_list:
            st.markdown("### 📋 បញ្ជីប្រតិបត្តិការទាំងអស់")
            df_display = []
            for idx, item in enumerate(reversed(st.session_state.sales_history)):
                df_display.append({
                    "ល.រ": len(st.session_state.sales_history) - idx,
                    "លេខវិក្កយបត្រ": item.get("inv_no"),
                    "កាលបរិច្ឆេទ": item.get("date"),
                    "អតិថិជន": item.get("customer"),
                    "សរុប ($)": f"${item.get('grand_total_usd', 0.0):.2f}"
                })
            st.dataframe(pd.DataFrame(df_display), use_container_width=True, hide_index=True)
            
            inv_list = [item.get("inv_no") for item in reversed(st.session_state.sales_history)]
            selected_inv = st.selectbox("ជ្រើសរើសលេខវិក្កយបត្រដើម្បី Preview/Print:", inv_list)
            selected_receipt_data = next((item for item in st.session_state.sales_history if item.get("inv_no") == selected_inv), None)

        with col_preview:
            st.markdown("### 👁️ មើលគំរូវិក្កយបត្រ")
            if selected_receipt_data:
                html_code = generate_receipt_html(selected_receipt_data)
                components.html(html_code, height=500, scrolling=True)

# ================================================================
# MODE 5: SALES REPORT
# ================================================================
elif main_mode == "📊 របាយការណ៍លក់ (Sales Report)":
    st.markdown("## 📊 របាយការណ៍លក់ប្រចាំថ្ងៃ/ខែ (Sales Analytics)")
    if not st.session_state.sales_history:
        st.info("💡 មិនទាន់មានទិន្នន័យលក់សម្រាប់បង្ហាញរបាយការណ៍នៅឡើយទេ!")
    else:
        total_invoices = len(st.session_state.sales_history)
        total_revenue_usd = sum(item.get("grand_total_usd", 0.0) for item in st.session_state.sales_history)
        total_revenue_khr = round(total_revenue_usd * EXCHANGE_RATE)

        m1, m2, m3 = st.columns(3)
        m1.metric("🧾 ចំនួនវិក្កយបត្រសរុប", f"{total_invoices}")
        m2.metric("💵 ចំណូលសរុប ($)", f"${total_revenue_usd:,.2f}")
        m3.metric("៛ ចំណូលសរុប (៛)", f"៛ {total_revenue_khr:,.0f}")

        st.markdown("---")
        item_rows = []
        for sale in st.session_state.sales_history:
            for it in sale.get("items", []):
                item_rows.append({
                    "Invoice": sale.get("inv_no"),
                    "Date": sale.get("date"),
                    "Customer": sale.get("customer"),
                    "Code": it.get("code"),
                    "Service Name": it.get("name"),
                    "Price": it.get("price"),
                    "Qty": it.get("qty"),
                    "Disc(%)": it.get("item_disc", 0),
                    "Subtotal": it.get("total")
                })
        st.dataframe(pd.DataFrame(item_rows), use_container_width=True, hide_index=True)
