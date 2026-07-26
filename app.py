# ----------------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling (កូដ CSS ដែលបានកែប្រែរួច)
# ----------------------------------------------------------------
st.set_page_config(
    page_title="OunLen SMR - Professional POS & Sales Report",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for UI Enhancement
st.markdown("""
<style>
    /* Background នៃ App ទាំងមូល */
    .stApp {
        background-color: #f1f5f9;
        font-family: 'Kantumruy Pro', 'Khmer OS Battambang', sans-serif;
        color: #0f172a;
    }
    
    /* 1. កែប្រែ Navigation Menu ខាងលើ (កន្លែងដែលមើលមិនច្បាស់) */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    div[data-testid="stRadio"] > div {
        background-color: #1e293b !important;
        padding: 8px 16px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] span {
        color: #ffffff !important; /* អក្សរពណ៌សច្បាស់ */
        font-size: 15px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] input:checked + div {
        background-color: #10b981 !important; /* ពណ៌ពេល Hover/Select */
    }

    /* 2. Circle Button Styling (ប៊ូតុងរង្វង់សេវាកម្ម) */
    div.stButton > button {
        border-radius: 50% !important;
        width: 125px !important;
        height: 125px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        /* ប្រើ Gradient បៃតងភ្លឺច្បាស់ */
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #ffffff !important; /* អក្សរពណ៌ស */
        text-shadow: 0px 1px 3px rgba(0, 0, 0, 0.8) !important; /* បន្ថែម Shadow លើអក្សរឱ្យកាន់តែច្បាស់ */
        border: 3px solid #ffffff !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
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
        box-shadow: 0 8px 15px rgba(0,0,0,0.3) !important;
        border-color: #f59e0b !important; /* Border ពណ៌លឿងពេល Hover */
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    }

    /* 3. POS Action Buttons (ប៊ូតុងមុខងារខាងស្តាំ) */
    .pos-btn div.stButton > button {
        border-radius: 8px !important;
        width: 100% !important;
        height: 48px !important;
        background: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-shadow: none !important;
    }
    
    .pos-btn div.stButton > button:hover {
        background: #1e293b !important;
        border-color: #3b82f6 !important;
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
        text-shadow: none !important;
    }

    /* 4. Customer Info Box */
    .customer-info-box {
        background-color: #047857;
        color: #ffffff;
        padding: 14px 16px;
        border-radius: 8px 8px 0px 0px;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* 5. Total Summary Box */
    .total-summary-header {
        background-color: #047857;
        color: #ffffff;
        padding: 10px 15px;
        font-weight: bold;
        font-size: 15px;
        border-radius: 8px 8px 0px 0px;
        margin-top: 10px;
    }
    
    .total-summary-body {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 15px;
        font-size: 13px;
        color: #0f172a;
        line-height: 1.8;
    }

    .summary-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }
    
    .grand-total-usd {
        color: #dc2626;
        font-size: 24px;
        font-weight: bold;
    }
    
    .grand-total-khr {
        color: #dc2626;
        font-size: 18px;
        font-weight: bold;
    }

    /* 6. Receipt Box Styling */
    .receipt-container {
        background: #fffbeb;
        border: 2px dashed #d97706;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        color: #0f172a;
    }

    /* 7. Metric Cards Styling */
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #059669;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .pos-footer-bar {
        background-color: #0f172a;
        color: #ffffff;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 12px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)
