import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# ----------------------------------------------------------------
# 🔗 ព័ត៌មានភ្ជាប់ទៅកាន់ Google Form ថ្មីស្រឡាង
FORM_URL = "https://forms.gle/TBkjty7pyhMPnMN58formResponse"

ENTRY_CODE = "entry.1990119949"     # លេខសម្រាប់ 'កូដកាត'
ENTRY_NAME = "entry.1171471622"     # លេខសម្រាប់ 'ឈ្មោះម្ចាស់កូដ'
ENTRY_COUNT = "entry.727798281"     # លេខសម្រាប់ 'ចំនួនអ្នកណែនាំ'
ENTRY_STATUS = "entry.1264942129"   # លេខសម្រាប់ 'ស្ថានភាព'
# ----------------------------------------------------------------

# 1. អានទិន្នន័យ Live ពី Google Sheets
try:
    original_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    if "edit?usp=sharing" in original_url:
        csv_url = original_url.replace("edit?usp=sharing", "gviz/tq?tqx=out:csv")
    elif "edit#" in original_url:
        csv_url = original_url.split("edit#")[0] + "gviz/tq?tqx=out:csv"
    else:
        csv_url = original_url
    
    df = pd.read_csv(csv_url)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីងក្នុង Secrets ឡើងវិញ។")
    st.stop()

if df is None or df.empty:
    df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនួនអ្នកណែនាំ", "ស្ថានភាព"])

df.columns = [str(col).strip() for col in df.columns]

if "Timestamp" in df.columns:
    df = df.drop(columns=["Timestamp"])

required_cols = ["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនួនអ្នកណែនាំ", "ស្ថានភាព"]
for col in required_cols:
    if col not in df.columns:
        df[col] = None

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជនថ្មី ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ KR001):").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    df["កូដកាត_clean"] = df["កូដកាត"].astype(str).str.strip().str.upper()
    valid_rows = df[df["កូដកាត_clean"] == input_code]
    
    if not valid_rows.empty:
        idx = valid_rows.index[-1] 
        status = str(df.loc[idx, "ស្ថានភាព"]).strip()
        
        if status == "បានប្រើរួច (Used)":
            st.error(f"❌ កូដ {input_code} នេះត្រូវបានប្រើប្រាស់ និងបើកកាដួ រួចរាល់ហើយ!")
        else:
            try:
                current_count = int(float(df.loc[idx, "ចំនួនអ្នកណែនាំ"])) + 1
            except:
                current_count = 1
                
            owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
            new_status = "គ្រប់លក្ខខណ្ឌ (Free)" if current_count >= 10 else "សកម្ម"
            
            form_data = {
                ENTRY_CODE: str(input_code),
                ENTRY_NAME: str(owner_name),
                ENTRY_COUNT: str(current_count),
                ENTRY_STATUS: str(new_status)
            }
            
            response = requests.post(FORM_URL, data=form_data)
            if response.status_code == 200:
                st.success(f"✅ បានរកឃើញកូដរបស់៖ **{owner_name}** និងរក្សារទិន្នន័យថ្មីរួចរាល់!")
                st.rerun()
            else:
                st.error(f"❌ មិនអាចកត់ត្រាពិន្ទុបានទេ! (Google Form Error Code: {response.status_code})")
    else:
        st.error("❌ មិនមានលេខកូដនេះក្នុងប្រព័ន្ធទេ!")

st.markdown("---")

# --- ផ្នែកទី ២៖ បង្កើតកូដថ្មី ---
st.header("➕ បង្កើតកូដថ្មី (សម្រាប់អតិថិជនទើបមកដំបូង)")
col1, col2 = st.columns(2)
with col1:
    new_code = st.text_input("បង្កើតលេខកូដថ្មី:").strip().upper()
with col2:
    new_name = st.text_input("ឈ្មោះអតិថិជន:")

if st.button("ចុះឈ្មោះកូដថ្មី"):
    if new_code and new_name:
        is_duplicate = False
        if "កូដកាត" in df.columns:
            for val in df["កូដកាត"].dropna().values:
                if str(val).strip().upper() == new_code:
                    is_duplicate = True
                    break
        
        if is_duplicate:
            st.error("❌ លេខកូដនេះមានរួចហើយ!")
        else:
            form_data = {
                ENTRY_CODE: str(new_code),
                ENTRY_NAME: str(new_name),
                ENTRY_COUNT: "0",
                ENTRY_STATUS: "សកម្ម"
            }
            
            # ព្យាយាមផ្ញើទៅកាន់ Google Form
            response = requests.post(FORM_URL, data=form_data)
            
            if response.status_code == 200:
                st.success(f"🎉 ចុះឈ្មោះកូដ {new_code} ជូនលោក/លោកស្រី {new_name} ជោគជ័យ!")
                st.balloons()
                st.rerun()
            else:
                # បង្ហាញកំហុសលម្អិតដើម្បីងាយស្រួលដោះស្រាយ
                st.error(f"❌ ហ្គូហ្គលហ្វមបដិសេធការបញ្ជូន! (Error Code: {response.status_code})")
                st.info("💡 ដំណោះស្រាយ៖ សូមចូលទៅកាន់ទំព័រ Settings របស់ Google Form រួចបិទការកំណត់ 'Limit to 1 response' និង 'Restrict to users...' ចោល។")
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យរួម ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")

if "កូដកាត_clean" in df.columns:
    df = df.drop(columns=["កូដកាត_clean"])

actual_data = df.dropna(subset=["កូដកាត"])

if not actual_data.empty:
    display_df = actual_data.drop_duplicates(subset=["កូដកាត"], keep="last")
    if "ចំនួនអ្នកណែនាំ" in display_df.columns:
        display_df["ភាគរយបញ្ចុះតម្លៃសន្សំបាន"] = display_df["ចំនួនអ្នកណែនាំ"].apply(
            lambda x: f"{int(float(x)) * 10}%" if pd.notnull(x) and str(x).replace('.0','').isdigit() and int(float(x)) < 10 else ("FREE 1 ដង" if pd.notnull(x) and str(x).replace('.0','').isdigit() and int(float(x)) >= 10 else "0%")
        )
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("📭 មិនទាន់មានទិន្នន័យអតិថិជននៅក្នុងប្រព័ន្ធឡើយ។ សូមសាកល្បងបង្កើតកូដថ្មីខាងលើ! 🥰")
