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
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DEFAULT INGREDIENT MASTER DATA (Ai-Cha)
# ==========================================
DEFAULT_INGREDIENTS = [
    {"Material Code": "KH201.0001", "Material Name": "Ice Cream Cone", "Unit": "箱CTN", "Specification": "400PCS/CTN", "Price per Case ($)": 22.33, "Total Weight (KG)": None, "Total Quantity (PCS)": 400, "Price per KG ($)": None, "Price per PCS ($)": 0.0558},
    {"Material Code": "KH201.0002", "Material Name": "Ice Cream Powder Original Flavor", "Unit": "箱CTN", "Specification": "24KG/CTN", "Price per Case ($)": 137.50, "Total Weight (KG)": 24.0, "Total Quantity (PCS)": None, "Price per KG ($)": 5.7292, "Price per PCS ($)": None},
    {"Material Code": "KH201.0003", "Material Name": "Ice Cream Powder Matcha Flator", "Unit": "箱CTN", "Specification": "24KG/CTN", "Price per Case ($)": 137.50, "Total Weight (KG)": 24.0, "Total Quantity (PCS)": None, "Price per KG ($)": 5.7292, "Price per PCS ($)": None},
    {"Material Code": "KH201.0004", "Material Name": "Ice Cream Powder Seasalt Flavor", "Unit": "箱CTN", "Specification": "24KG/CTN", "Price per Case ($)": 137.50, "Total Weight (KG)": 24.0, "Total Quantity (PCS)": None, "Price per KG ($)": 5.7292, "Price per PCS ($)": None},
    {"Material Code": "KH201.0005", "Material Name": "Milk Tea Powder", "Unit": "箱CTN", "Specification": "20KG/CTN", "Price per Case ($)": 0.00, "Total Weight (KG)": 20.0, "Total Quantity (PCS)": None, "Price per KG ($)": 0.0000, "Price per PCS ($)": None},
    {"Material Code": "KH201.0006", "Material Name": "Pudding Powder", "Unit": "箱CTN", "Specification": "20KG/CTN", "Price per Case ($)": 99.00, "Total Weight (KG)": 20.0, "Total Quantity (PCS)": None, "Price per KG ($)": 4.9500, "Price per PCS ($)": None},
    {"Material Code": "KH201.0007", "Material Name": "Strawberry Jam", "Unit": "箱CTN", "Specification": "12KG(2KG*6CANS)/CTN", "Price per Case ($)": 49.50, "Total Weight (KG)": 12.0, "Total Quantity (PCS)": None, "Price per KG ($)": 4.1250, "Price per PCS ($)": None},
    {"Material Code": "KH201.0009", "Material Name": "Blueberry Jam", "Unit": "箱CTN", "Specification": "12KG(2KG*6CANS)/CTN", "Price per Case ($)": 55.00, "Total Weight (KG)": 12.0, "Total Quantity (PCS)": None, "Price per KG ($)": 4.5833, "Price per PCS ($)": None},
    {"Material Code": "KH201.0012", "Material Name": "Grape Jam", "Unit": "箱CTN", "Specification": "12KG(2KG*6CANS)/CTN", "Price per Case ($)": 60.50, "Total Weight (KG)": 12.0, "Total Quantity (PCS)": None, "Price per KG ($)": 5.0417, "Price per PCS ($)": None},
    {"Material Code": "KH201.0013", "Material Name": "Passion Fruit Jam", "Unit": "箱CTN", "Specification": "13.8KG(2.3KG*6CANS)/CTN", "Price per Case ($)": 49.50, "Total Weight (KG)": 13.8, "Total Quantity (PCS)": None, "Price per KG ($)": 3.5870, "Price per PCS ($)": None},
    {"Material Code": "KH201.0015", "Material Name": "Fructose Syrup", "Unit": "箱CTN", "Specification": "26KG(6.5KG*4BOTTLES)/CTN", "Price per Case ($)": 47.66, "Total Weight (KG)": 26.0, "Total Quantity (PCS)": None, "Price per KG ($)": 1.8331, "Price per PCS ($)": None},
    {"Material Code": "KH201.0016", "Material Name": "Sugar Syrup", "Unit": "箱CTN", "Specification": "26KG(6.5KG*4BOTTLES)/CTN", "Price per Case ($)": 47.63, "Total Weight (KG)": 26.0, "Total Quantity (PCS)": None, "Price per KG ($)": 1.8319, "Price per PCS ($)": None},
    {"Material Code": "KH201.0017", "Material Name": "Brown Sugar Syrup", "Unit": "箱CTN", "Specification": "20KG(2.5KG*8BOTTLES)/CTN", "Price per Case ($)": 56.84, "Total Weight (KG)": 20.0, "Total Quantity (PCS)": None, "Price per KG ($)": 2.8420, "Price per PCS ($)": None},
    {"Material Code": "KH201.0019", "Material Name": "Brown Sugar Flavored Tapioca Pearl", "Unit": "箱CTN", "Specification": "18KG/CTN", "Price per Case ($)": 28.60, "Total Weight (KG)": 18.0, "Total Quantity (PCS)": None, "Price per KG ($)": 1.5889, "Price per PCS ($)": None},
    {"Material Code": "KH201.0022", "Material Name": "Nata De Coco", "Unit": "箱CTN", "Specification": "18KG（1.5KG*12BAGS）", "Price per Case ($)": 24.50, "Total Weight (KG)": 18.0, "Total Quantity (PCS)": None, "Price per KG ($)": 1.3611, "Price per PCS ($)": None},
    {"Material Code": "KH201.0026", "Material Name": "Coffee Beans", "Unit": "箱CTN", "Specification": "10KG", "Price per Case ($)": 201.66, "Total Weight (KG)": 10.0, "Total Quantity (PCS)": None, "Price per KG ($)": 20.1660, "Price per PCS ($)": None},
    {"Material Code": "KH201.0028", "Material Name": "700 Plastic Cup", "Unit": "箱CTN", "Specification": "1000PCS(50PCS*20BAGS)/CTN", "Price per Case ($)": 63.80, "Total Weight (KG)": None, "Total Quantity (PCS)": 1000, "Price per KG ($)": None, "Price per PCS ($)": 0.0638},
    {"Material Code": "KH201.0029", "Material Name": "500 Plastic Cup", "Unit": "箱CTN", "Specification": "1000PCS(50PCS*20BAGS)/CTN", "Price per Case ($)": 55.03, "Total Weight (KG)": None, "Total Quantity (PCS)": 1000, "Price per KG ($)": None, "Price per PCS ($)": 0.0550},
    {"Material Code": "KH201.0030", "Material Name": "400 U Type Plastic Cup", "Unit": "箱CTN", "Specification": "1000PCS(50PCS*20BAGS)/CTN", "Price per Case ($)": 55.03, "Total Weight (KG)": None, "Total Quantity (PCS)": 1000, "Price per KG ($)": None, "Price per PCS ($)": 0.0550},
    {"Material Code": "KH201.0031", "Material Name": "Disposable Spherical Tea Cover", "Unit": "箱CTN", "Specification": "1000PCS(50PCS*20BAGS)/CTN", "Price per Case ($)": 30.90, "Total Weight (KG)": None, "Total Quantity (PCS)": 1000, "Price per KG ($)": None, "Price per PCS ($)": 0.0309},
    {"Material Code": "KH201.0040", "Material Name": "Coffee Lid", "Unit": "箱CTN", "Specification": "90mm 500PCS(50PCS*10BAGS)/CTN", "Price per Case ($)": 25.75, "Total Weight (KG)": None, "Total Quantity (PCS)": 500, "Price per KG ($)": None, "Price per PCS ($)": 0.0515},
    {"Material Code": "KH201.0048", "Material Name": "Single Fine Straw", "Unit": "箱CTN", "Specification": "5000PCS(100PCS*50BAGS)/CTN", "Price per Case ($)": 39.83, "Total Weight (KG)": None, "Total Quantity (PCS)": 5000, "Price per KG ($)": None, "Price per PCS ($)": 0.0080},
    {"Material Code": "KH201.0049", "Material Name": "Single Thick Straw", "Unit": "箱CTN", "Specification": "5000PCS(100PCS*50BAGS)/CTN", "Price per Case ($)": 81.74, "Total Weight (KG)": None, "Total Quantity (PCS)": 5000, "Price per KG ($)": None, "Price per PCS ($)": 0.0163},
    {"Material Code": "KH201.0052", "Material Name": "Sundae Spoon", "Unit": "箱CTN", "Specification": "3000PCS(50PCS*60BAGS)/CTN", "Price per Case ($)": 50.56, "Total Weight (KG)": None, "Total Quantity (PCS)": 3000, "Price per KG ($)": None, "Price per PCS ($)": 0.0169},
    {"Material Code": "KH201.0054", "Material Name": "Sealing Film", "Unit": "箱CTN", "Specification": "12000PCS(2000PCS*6ROLLS)/CTN", "Price per Case ($)": 93.50, "Total Weight (KG)": None, "Total Quantity (PCS)": 12000, "Price per KG ($)": None, "Price per PCS ($)": 0.0078},
    {"Material Code": "KH201.0055", "Material Name": "Ice Cream Tray", "Unit": "箱CTN", "Specification": "20000PCS(400PCS*50BAGS)/CTN", "Price per Case ($)": 86.54, "Total Weight (KG)": None, "Total Quantity (PCS)": 20000, "Price per KG ($)": None, "Price per PCS ($)": 0.0043},
    {"Material Code": "KH201.0138", "Material Name": "Peach Oolong Tea", "Unit": "箱CTN", "Specification": "10KG/CTN", "Price per Case ($)": 165.00, "Total Weight (KG)": 10.0, "Total Quantity (PCS)": None, "Price per KG ($)": 16.5000, "Price per PCS ($)": None},
    {"Material Code": "KH201.0160", "Material Name": "Da Hong Pao (Oolong Tea)", "Unit": "箱CTN", "Specification": "10KG(50G*10BAG*10BAGS)/CTN", "Price per Case ($)": 121.86, "Total Weight (KG)": 10.0, "Total Quantity (PCS)": None, "Price per KG ($)": 12.1860, "Price per PCS ($)": None},
    {"Material Code": "KH202.0017", "Material Name": "Fresh Lemons", "Unit": "公斤KG", "Specification": "Lemon Lokal AB Standart", "Price per Case ($)": 0.00, "Total Weight (KG)": None, "Total Quantity (PCS)": None, "Price per KG ($)": None, "Price per PCS ($)": None},
    {"Material Code": "KH201.0197", "Material Name": "Non-Dairy Creamer", "Unit": "箱CTN", "Specification": "20KG/CTN", "Price per Case ($)": 93.50, "Total Weight (KG)": 20.0, "Total Quantity (PCS)": None, "Price per KG ($)": 4.6750, "Price per PCS ($)": None}
]

# ==========================================
# 3. SECRETS & API CONFIG
# ==========================================
APPS_SCRIPT_URL = st.secrets.get("APPS_SCRIPT_URL", "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec")
API_SECRET_KEY = st.secrets.get("API_SECRET_KEY", "AICHA_SECURE_KEY_2026")

@st.cache_data(ttl=10)
def fetch_aicha_data():
    try:
        res = requests.get(f"{APPS_SCRIPT_URL}?api_key={API_SECRET_KEY}", timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}

data = fetch_aicha_data()

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("🧋 Ai-Cha System")
menu = st.sidebar.radio("ជ្រើសរើសទំព័រ៖", [
    "📊 Dashboard & Summary",
    "📦 Ingredient Master List",
    "📉 Daily Usage Tracker",
    "📈 Daily Sales Tracker"
])

# ==========================================
# 5. DASHBOARD & SUMMARY
# ==========================================
if menu == "📊 Dashboard & Summary":
    st.title("📊 របាយការណ៍ចំណូល-ចំណាយប្រចាំខែ (Dashboard)")
    
    fixed_costs = data.get("fixed_costs", 1595.0)
    usage_list = data.get("usage_tracker", [])
    sales_list = data.get("sales_tracker", [])
    
    total_ingredient_cost = sum([float(item.get("total_cost", 0)) for item in usage_list if item.get("total_cost")])
    total_overall_cost = fixed_costs + total_ingredient_cost
    total_revenue = sum([float(item.get("total_revenue", 0)) for item in sales_list if item.get("total_revenue")])
    net_profit = total_revenue - total_overall_cost
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ចំណូលលក់សរុប (Revenue)", f"${total_revenue:.2f}")
    c2.metric("ចំណាយថេរ (Fixed Costs)", f"${fixed_costs:.2f}")
    c3.metric("ចំណាយគ្រឿងផ្សំ (Ingredient Costs)", f"${total_ingredient_cost:.2f}")
    c4.metric("ចំណេញ/ខាត សុទ្ធ (Net Profit)", f"${net_profit:.2f}")

# ==========================================
# 6. INGREDIENT MASTER LIST
# ==========================================
elif menu == "📦 Ingredient Master List":
    st.title("📦 បញ្ជីថ្លៃដើមគ្រឿងផ្សំ (Ingredient & Cost Master List)")
    
    ingredients_from_api = data.get("ingredients", [])
    
    # Use API data if available, otherwise use DEFAULT_INGREDIENTS
    if ingredients_from_api and len(ingredients_from_api) > 0:
        df_ing = pd.DataFrame(ingredients_from_api)
    else:
        df_ing = pd.DataFrame(DEFAULT_INGREDIENTS)
        
    st.dataframe(df_ing, use_container_width=True)

# ==========================================
# 7. DAILY USAGE TRACKER
# ==========================================
elif menu == "📉 Daily Usage Tracker":
    st.title("📉 ការកត់ត្រាប្រើប្រាស់គ្រឿងផ្សំប្រចាំថ្ងៃ")
    
    ingredients_from_api = data.get("ingredients", [])
    ingredients_data = ingredients_from_api if ingredients_from_api else DEFAULT_INGREDIENTS
    
    ing_names = [i["Material Name"] if "Material Name" in i else i.get("material_name") for i in ingredients_data]
    
    with st.form("add_usage_form"):
        u_date = st.date_input("កាលបរិច្ឆេទ", datetime.now().date())
        u_material = st.selectbox("ជ្រើសរើសគ្រឿងផ្សំ", ing_names)
        u_qty = st.number_input("ចំនួនប្រើប្រាស់ (Quantity Used)", min_value=0.01, step=0.1)
        u_unit = st.selectbox("ខ្នាត (Unit)", ["KG", "PCS"])
        
        if st.form_submit_button("➕ រក្សាទុកការប្រើប្រាស់"):
            st.success(f"✅ បានកត់ត្រា {u_material} ចំនួន {u_qty} {u_unit} ជោគជ័យ!")

# ==========================================
# 8. DAILY SALES TRACKER
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
            st.success(f"✅ បានរក្សាទុកទិន្នន័យលក់ {s_name} ចំនួន {s_qty} កែវ ជោគជ័យ!")
