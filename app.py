import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# ----------------------------------------------------------------
# 🔗 ព័ត៌មានភ្ជាប់ទៅកាន់ Google Form របស់ហាង អូនឡែន សម្រស់
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScvhuVjcIYkX61RDDYvu3UuYNoHiQORJuhH5Tb1yL2CWEjUsw/formResponse"

ENTRY_CODE = "entry.236683526"      # លេខសម្រាប់ 'កូដកាត'
ENTRY_NAME = "entry.1741541315"    # លេខសម្រាប់ 'ឈ្មោះម្ចាស់កូដ'
ENTRY_COUNT = "entry.1593503525"   # លេខសម្រាប់ 'ចំនូនអ្នកណែនាំ'
ENTRY_STATUS = "entry.1444218765"  # លេខសម្រាប់ 'ស្ថានភាព'
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
        
    raw_df = pd.read_csv(csv_url)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីងក្នុង Secrets ឡើងវិញ។")
    st.stop()

# 🛠️ វិធីសាស្ត្រពិសេស៖ ចាប់យកទិន្នន័យតាមលំដាប់ជួរ (Columns) ការពារបញ្ហាខុសអក្ខរាវិរុទ្ធក្នុង Sheets
if raw_df is not None and not raw_df.empty:
    # បើមានជាប់ជួរ Timestamp (ពេលវេលា) របស់ Google Form នៅជួរទី១ ត្រូវដកចេញ
    if "Timestamp" in raw_df.columns or "ពេលវេលា" in str(raw_df.columns[0]):
        raw_df = raw_df.iloc[:, 1:]
        
    # បង្កើតតារាងថ្មីដោយកំណត់ឈ្មោះ Column ឱ្យស្តង់ដារ ទោះក្នុង Sheets បងសរសេរខុសក៏មិនអីដែរ
    df = pd.DataFrame()
    cols_count = len(raw_df.columns)
    
    df["កូដកាត"] = raw_df.iloc[:, 0] if cols_count > 0 else None
    df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 1] if cols_count > 1 else None
    df["ចំនូនអ្នកណែនាំ"] = raw_df.iloc[:, 2] if cols_count > 2 else 0
    df["ស្ថានភាព"] = raw_df.iloc[:, 3] if cols_count > 3 else "សកម្ម"
else:
    df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនូនអ្នកណែនាំ", "ស្ថានភាព"])

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជនថ្មី ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ KR001):", key="verify_input").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    if not df.empty and df["កូដកាត"].notnull().any():
        df["កូដកាត_clean"] = df["កូដកាត"].astype(str).str.strip().str.upper()
        valid_rows = df[df["កូដកាត_clean"] == input_code]
        
        if not valid_rows.empty:
            idx = valid_rows.index[-1] # ចាប់យកជួរចុងក្រោយបង្អស់
            
            status = str(df.loc[idx, "ស្ថានភាព"]).strip()
            if status == "បានប្រើរួច (Used)":
                st.error(f"❌ កូដ {input_code} នេះត្រូវបានប្រើប្រាស់ និងបើកកាដូរួចរាល់ហើយ!")
            else:
                try:
                    current_count = int(float(df.loc[idx, "ចំនូនអ្នកណែនាំ"])) + 1
                except:
                    current_count = 1
                    
                owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                new_status = "គ្រប់លក្ខខណ្ឌ (Free)" if current_count >= 10 else "សកម្ម"
                
                # បញ្ជូនទិន្នន័យថ្មីទៅកាន់ Google Form 
                form_data = {
                    ENTRY_CODE: input_code,
                    ENTRY_NAME: owner_name,
                    ENTRY_COUNT: current_count,
                    ENTRY_STATUS: new_status
                }
                
                response = requests.post(FORM_URL, data=form_data)
                
                if response.status_code == 200:
                    st.success(f"✅ បានរកឃើញកូដរបស់៖ **{owner_name}**")
                    st.info(f"📈 ចំនួនអ្នកណែនាំបច្ចុប្បន្ន៖ **{current_count} នាក់** (ទទួលបានការបញ្ចុះតម្លៃ {current_count * 10}%)")
                    if current_count >= 10:
                        st.balloons()
                        st.warning(f"🎉 ម្ចាស់កូដ **{owner_name}** ណែនាំគ្រប់ ១០នាក់ហើយ! គាត់ទទួលបាន **សេវាកម្មហ្វ្រី ១ដង** នៅពេលមកលើកក្រោយ។")
                    st.info("💡 រក្សាទុកជោគជ័យ! សូម Refresh កម្មវិធី ដើម្បីទាញទិន្នន័យថ្មី។")
                else:
                    st.error("❌ មានបញ្ហាក្នុងការរក្សាទុកទិន្នន័យត្រឡប់ទៅ Sheets!")
        else:
            st.error(f"❌ មិនមានលេខកូដ {input_code} នេះក្នុងប្រព័ន្ធទេ!")
    else:
        st.error("❌ ប្រព័ន្ធទិន្នន័យទទេរ! សូមបង្កើតកូដថ្មីខាងក្រោមជាមុនសិន។")

st.markdown("---")

# --- ផ្នែកទី ២៖ បង្កើតកូដថ្មី ---
st.header("➕ បង្កើតកូដថ្មី (សម្រាប់អតិថិជនទើបមកដំបូង)")
col1, col2 = st.columns(2)
with col1:
    new_code = st.text_input("បង្កើតលេខកូដថ្មី (ឧទាហរណ៍៖ KR001):", key="new_code_input").strip().upper()
with col2:
    new_name = st.text_input("ឈ្មោះអតិថិជន:", key="new_name_input")

if st.button("ចុះឈ្មោះកូដថ្មី"):
    if new_code and new_name:
        is_duplicate = False
        if not df.empty and df["កូដកាត"].notnull().any():
            df["កូដកាត_str"] = df["កូដកាត"].astype(str).str.strip().str.upper()
            if new_code in df["កូដកាត_str"].values:
                is_duplicate = True
                
        if is_duplicate:
            st.error("❌ លេខកូដនេះមានរួចហើយ!")
        else:
            # បញ្ជូនទិន្នន័យបង្កើតថ្មីទៅកាន់ Google Form
            form_data = {
                ENTRY_CODE: new_code,
                ENTRY_NAME: new_name,
                ENTRY_COUNT: 0,
                ENTRY_STATUS: "សកម្ម"
            }
            response = requests.post(FORM_URL, data=form_data)
            
            if response.status_code == 200:
                st.success(f"🎉 ចុះឈ្មោះកូដ {new_code} ជូនលោក/លោកស្រី {new_name} ជោគជ័យ!")
                st.balloons()
                st.info("💡 បង្កើតកូដជោគជ័យ! សូមរង់ចាំ ១ ទៅ ២ នាទី រួចធ្វើការ Refresh កម្មវិធីដើម្បីឱ្យទិន្នន័យលោតឡើងក្នុងតារាង។")
            else:
                st.error("❌ មិនអាចបញ្ជូនទិន្នន័យទៅកាន់ Google Sheets បានទេ!")
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យរួម ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")

if not df.empty and df["កូដកាត"].notnull().any():
    actual_data = df.dropna(subset=["កូដកាត"])
    # សម្អាតទិន្នន័យមុនបង្ហាញ
    actual_data["កូដកាត"] = actual_data["កូដកាត"].astype(str).str.strip().str.upper()
    
    # លុបជួរដែលជាន់គ្នា ចាប់យកតែទិន្នន័យចុងក្រោយបង្អស់មកបង្ហាញ
    display_df = actual_data.drop_duplicates(subset=["កូដកាត"], keep="last")
    
    # បង្កើត Column បញ្ចុះតម្លៃ
    def calculate_discount(x):
        try:
            val = int(float(x))
            return f"{val * 10}%" if val < 10 else "FREE 1 ដង"
        except:
            return "0%"
            
    display_df["ភាគរយបញ្ចុះតម្លៃសន្សំបាន"] = display_df["ចំនូនអ្នកណែនាំ"].apply(calculate_discount)
    
    # រៀបចំ Columns ឱ្យស្អាតសម្រាប់បង្ហាញ
    final_cols = ["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនូនអ្នកណែនាំ", "ស្ថានភាព", "ភាគរយបញ្ចុះតម្លៃសន្សំបាន"]
    st.dataframe(display_df[final_cols], use_container_width=True)
else:
    st.info("📭 មិនទាន់មានទិន្នន័យអតិថិជននៅក្នុងប្រព័ន្ធឡើយ។ សូមសាកល្បងបង្កើតកូដថ្មីខាងលើ! 🥰")
