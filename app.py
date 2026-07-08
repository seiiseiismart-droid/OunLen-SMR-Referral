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
ENTRY_COUNT = "entry.1593503525"   # លេខសម្រាប់ 'ចំនំនួនអ្នកណែនាំ'
ENTRY_STATUS = "entry.1444218765"  # លេខសម្រាប់ 'ស្ថានភាព'
# ----------------------------------------------------------------

# 1. អានទិន្នន័យ Live ពី Google Sheets
try:
    original_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    if "docs.google.com/spreadsheets" in original_url:
        if "edit" in original_url:
            csv_url = original_url.split("/edit")[0] + "/export?format=csv"
        elif "pubhtml" in original_url:
            csv_url = original_url.replace("pubhtml", "pub?output=csv")
        else:
            csv_url = original_url
    else:
        csv_url = original_url
        
    raw_df = pd.read_csv(csv_url)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីងក្នុង Secrets ឡើងវិញ។")
    st.stop()

# បង្កើតតារាងស្តង់ដារសម្រាប់ដំណើរការក្នុងប្រព័ន្ធ (កែសម្រួលអក្ខរាវិរុទ្ធឱ្យត្រូវតាម Sheets របស់បង)
df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព"])

if raw_df is not None and not raw_df.empty:
    raw_df.columns = [str(col).strip() for col in raw_df.columns]
    
    if "Timestamp" in raw_df.columns:
        raw_df = raw_df.drop(columns=["Timestamp"])
    elif "ពេលវេលា" in str(raw_df.columns[0]):
        raw_df = raw_df.iloc[:, 1:]
        
    cols_count = len(raw_df.columns)
    if cols_count >= 1: df["កូដកាត"] = raw_df.iloc[:, 0]
    if cols_count >= 2: df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 1]
    if cols_count >= 3: df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 2]
    if cols_count >= 4: df["ស្ថានភាព"] = raw_df.iloc[:, 3]

if not df.empty:
    df = df[~df["កូដកាត"].astype(str).str.contains("<DIV|<SPAN|html|none", case=False, na=True)]

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជនថ្មី ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ KR001):", key="verify_input").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    if not df.empty and df["កូដកាត"].notnull().any():
        df["កូដកាត_clean"] = df["កូដកាត"].astype(str).str.strip().str.upper()
        valid_rows = df[df["កូដកាត_clean"] == input_code]
        
        if not valid_rows.empty:
            idx = valid_rows.index[-1]
            status = str(df.loc[idx, "ស្ថានភាព"]).strip()
            
            if status == "បានប្រើរួច (Used)":
                st.error(f"❌ កូដ {input_code} នេះត្រូវបានប្រើប្រាស់ និងបើកកាដូរួចរាល់ហើយ!")
            else:
                try:
                    current_count = int(float(df.loc[idx, "ចំនំនួនអ្នកណែនាំ"])) + 1
                except:
                    current_count = 1
                    
                owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                new_status = "គ្រប់លក្ខខណ្ឌ (Free)" if current_count >= 10 else "សកម្ម"
                
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
                    st.info("💡 រក្សាទុកជោគជ័យ! សូមបុក Refresh (F5) កម្មវិធីឡើងវិញ ដើម្បីទាញទិន្នន័យថ្មី។")
                else:
                    st.error("❌ មានបញ្ហាក្នុងការតភ្ជាប់ទៅកាន់ Google Form! សូមពិនិត្យមើល Entry IDs ក្នុងកូដឡើងវិញ។")
        else:
            st.error(f"❌ មិនមានលេខកូដ {input_code} នេះក្នុងប្រព័ន្ធទេ!")
    else:
        st.error("❌ ប្រព័ន្ធទិន្នន័យទទេរ! សូមបង្កើតកូដថ្មីសាកល្បងខាងក្រោមជាមុនសិន។")

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
                st.info("💡 បង្កើតកូដជោគជ័យ! សូមរង់ចាំបន្តិច រួចធ្វើការ Refresh កម្មវិធី ដើម្បីឱ្យទិន្នន័យបង្ហាញក្នុងតារាង។")
            else:
                st.error("❌ មិនអាចបញ្ជូនទិន្នន័យទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើល FORM_URL និង Entry IDs ឡើងវិញ។")
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យរួម ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")

if not df.empty and df["កូដកាត"].notnull().any():
    actual_data = df.dropna(subset=["កូដកាត"])
    actual_data["កូដកាត"] = actual_data["កូដកាត"].astype(str).str.strip().str.upper()
    
    display_df = actual_data.drop_duplicates(subset=["កូដកាត"], keep="last")
    
    def calculate_discount(x):
        try:
            val = int(float(x))
            return f"{val * 10}%" if val < 10 else "FREE 1 ដង"
        except:
            return "0%"
            
    display_df["ភាគរយបញ្ចុះតម្លៃសន្សំបាន"] = display_df["ចំនំនួនអ្នកណែនាំ"].apply(calculate_discount)
    
    final_cols = ["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព", "ភាគរយបញ្ចុះតម្លៃសន្សំបាន"]
    st.dataframe(display_df[final_cols].reset_index(drop=True), use_container_width=True)
else:
    st.info("📭 មិនទាន់មានទិន្នន័យអតិថិជននៅក្នុងប្រព័ន្ធឡើយ។ 🥰")
