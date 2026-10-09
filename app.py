import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="Ai-Cha - របាយការណ៍ និងគ្រប់គ្រងស្តុក",
    page_icon="🧋",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@300;400;600;700&display=swap');
    * { font-family: 'Kantumruy Pro', sans-serif; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .metric-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #38bdf8;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECRETS & API CONFIG
# ==========================================
APPS_SCRIPT_URL = st.secrets.get("APPS_SCRIPT_URL", "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec")
API_SECRET_KEY = st.secrets.get("API_SECRET_KEY", "AICHA_SECURE_KEY_2026")

@st.cache_data(ttl=10)
def fetch_aicha_data():
    try:
        res = requests.get(f"{APPS_SCRIPT_URL}?api_key={API_SECRET_KEY}", timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"កំហុសក្នុងការទាញយកទិន្នន័យ៖ {e}")
    return {}

data = fetch_aicha_data()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("🧋 Ai-Cha System")
menu = st.sidebar.radio("ជ្រើសរើសទំព័រ៖", [
    "📊 Dashboard & Summary",
    "📦 Ingredient Master List",
    "📉 Daily Usage Tracker",
    "📈 Daily Sales Tracker"
])

# ==========================================
# 4. DASHBOARD & SUMMARY
# ==========================================
if menu == "📊 Dashboard & Summary":
    st.title("📊 របាយការណ៍ចំណូល-ចំណាយប្រចាំខែ (Dashboard)")
    
    fixed_costs = data.get("fixed_costs", 1595.0)
    usage_list = data.get("usage_tracker", [])
    sales_list = data.get("sales_tracker", [])
    
    # Calculate Total Ingredient Cost
    total_ingredient_cost = sum([float(item.get("total_cost", 0)) for item in usage_list if item.get("total_cost")])
    total_overall_cost = fixed_costs + total_ingredient_cost
    
    # Calculate Total Revenue
    total_revenue = sum([float(item.get("total_revenue", 0)) for item in sales_list if item.get("total_revenue")])
    net_profit = total_revenue - total_overall_cost
    
    # Metric Display
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ចំណូលលក់សរុប (Revenue)", f"${total_revenue:.2f}")
    c2.metric("ចំណាយថេរ (Fixed Costs)", f"${fixed_costs:.2f}")
    c3.metric("ចំណាយគ្រឿងផ្សំ (Ingredient Costs)", f"${total_ingredient_cost:.2f}")
    c4.metric("ចំណេញ/ខាត សុទ្ធ (Net Profit)", f"${net_profit:.2f}")
    
    st.markdown("---")
    st.subheader("📌 ព័ត៌មានលម្អិតចំណាយថេរប្រចាំខែ (Fixed Operational Costs)")
    fixed_df = pd.DataFrame([
        {"Expense Category": "Staff (បុគ្គលិក ៤នាក់)", "Monthly Cost": "$800.00"},
        {"Expense Category": "Building Rent (ជួលអគារ)", "Monthly Cost": "$300.00"},
        {"Expense Category": "Utilities (ទឹកភ្លើង)", "Monthly Cost": "$300.00"},
        {"Expense Category": "POS System (ប្រព័ន្ធ POS)", "Monthly Cost": "$25.00"},
        {"Expense Category": "Miscellaneous / Other Expenses", "Monthly Cost": "$170.00"},
    ])
    st.table(fixed_df)

# ==========================================
# 5. INGREDIENT MASTER LIST
# ==========================================
elif menu == "📦 Ingredient Master List":
    st.title("📦 បញ្ជីថ្លៃដើមគ្រឿងផ្សំ (Ingredient & Cost Master List)")
    ingredients = data.get("ingredients", [])
    
    if ingredients:
        df_ing = pd.DataFrame(ingredients)
        st.dataframe(df_ing, use_container_width=True)
    else:
        st.info("មិនទាន់មានទិន្នន័យគ្រឿងផ្សំទេ")

# ==========================================
# 6. DAILY USAGE TRACKER
# ==========================================
elif menu == "📉 Daily Usage Tracker":
    st.title("📉 ការកត់ត្រាប្រើប្រាស់គ្រឿងផ្សំប្រចាំថ្ងៃ")
    
    ingredients = data.get("ingredients", [])
    ing_options = {i["material_name"]: i for i in ingredients} if ingredients else {}
    
    with st.form("add_usage_form"):
        u_date = st.date_input("កាលបរិច្ឆេទ", datetime.now().date())
        u_material = st.selectbox("ជ្រើសរើសគ្រឿងផ្សំ", list(ing_options.keys()) if ing_options else ["None"])
        u_qty = st.number_input("ចំនួនប្រើប្រាស់ (Quantity Used)", min_value=0.01, step=0.1)
        u_unit = st.selectbox("ខ្នាត (Unit)", ["KG", "PCS"])
        
        if st.form_submit_button("➕ រក្សាទុកការប្រើប្រាស់"):
            selected_ing = ing_options.get(u_material, {})
            unit_cost = 0.0
            if u_unit == "KG":
                unit_cost = float(selected_ing.get("price_per_kg", 0) or 0)
            else:
                unit_cost = float(selected_ing.get("price_per_pcs", 0) or 0)
                
            tot_cost = u_qty * unit_cost
            
            payload = {
                "api_key": API_SECRET_KEY,
                "action": "add_daily_usage",
                "date": str(u_date),
                "material_name": u_material,
                "quantity_used": u_qty,
                "unit": u_unit,
                "unit_cost": unit_cost,
                "total_cost": tot_cost
            }
            res = requests.post(APPS_SCRIPT_URL, json=payload)
            if res.status_code == 200:
                st.success("✅ បានកត់ត្រាការប្រើប្រាស់ជោគជ័យ!")
                st.cache_data.clear()

# ==========================================
# 7. DAILY SALES TRACKER
# ==========================================
elif menu == "📈 Daily Sales Tracker":
    st.title("📈 កត់ត្រាការលក់ចេញប្រចាំថ្ងៃ")
    
    with st.form("add_sales_form"):
        s_date = st.date_input("កាលបរិច្ឆេទ", datetime.now().date())
        s_code = st.text_input("កូដទំនិញ (Item Code)")
        s_name = st.text_input("ឈ្មោះភេសជ្ជៈ/ទំនិញ (Item Name)")
        s_price = st.number_input("តម្លៃ/កែវ ($)", min_value=0.0, step=0.25)
        s_qty = st.number_input("ចំនួនលក់ចេញ (Quantity Sold)", min_value=1, step=1)
        
        if st.form_submit_button("➕ រក្សាទុកទិន្នន័យលក់"):
            tot_rev = s_price * s_qty
            payload = {
                "api_key": API_SECRET_KEY,
                "action": "add_daily_sales",
                "date": str(s_date),
                "item_code": s_code,
                "item_name": s_name,
                "unit_price": s_price,
                "quantity_sold": s_qty,
                "total_revenue": tot_rev
            }
            res = requests.post(APPS_SCRIPT_URL, json=payload)
            if res.status_code == 200:
                st.success("✅ បានរក្សាទុកទិន្នន័យលក់ជោគជ័យ!")
                st.cache_data.clear()
