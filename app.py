import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# ----------------------------------------------------------------
# 🔗 ព័ត៌មានតភ្ជាប់ទៅកាន់ Google Form (សម្រាប់បញ្ជូនទិន្នន័យ)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScvhuVjcIYkX61RDDYvu3UuYNoHiQORJuhH5Tb1yL2CWEjUsw/formResponse"

ENTRY_CODE = "entry.236683526"      # ប្រអប់៖ កូដកាត
ENTRY_NAME = "entry.1741541315"    # ប្រអប់៖ ឈ្មោះម្ចាស់កូដ
ENTRY_COUNT = "entry.1593503525"   # ប្រអប់៖ ចំនំនួនអ្នកណែនាំ
ENTRY_STATUS = "entry.1444218765"  # ប្រអប់៖ ស្ថានភាព
# ----------------------------------------------------------------

# 1. អានទិន្នន័យ Live ពី Google Sheets តាមរយៈលីង CSV ផ្ទាល់
try:
    # ទាញយកលីងសន្លឹកកិច្ចការពី Secrets
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # បំប្លែងលីងទៅជាទម្រង់ទាញយក CSV អូតូ
    if "docs.google.com/spreadsheets" in spreadsheet_url:
        spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
    else:
        csv_url = spreadsheet_url

    # អានទិន្នន័យមកដាក់ក្នុង DataFrame
    raw_df = pd.read_csv(csv_url)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីងក្នុង Secrets ឡើងវិញ។")
    st.stop()

# បង្កើតរចនាសម្ព័ន្ធតារាងឱ្យត្រូវ ១០០% ជាមួយ Sheets របស់បង
df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព"])

if raw_df is not None and not raw_df.empty:
    # សម្អាតដកឃ្លាក្បាលជួរឈរ
    raw_df.columns = [str(col).strip() for col in raw_df.columns]
    
    # ចាប់យកទិន្នន័យផ្គូផ្គងតាមលំដាប់ជួរឈរ (ជួរទី២=កូដកាត, ទី៣=ឈ្មោះ, ទី៤=ចំនួន, ទី៥=ស្ថានភាព)
    # មិនខ្វល់ថាក្បាលជួរឈរសរសេរអក្សរអ្វីទេ គឺចាប់តាមលំដាប់លំដោយជួរតែម្ដង
    cols_count = len(raw_df.columns)
    if cols_count >= 2: df["កូដកាត"] = raw_df.iloc[:, 1]
    if cols_count >= 3: df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 2]
    if cols_count >= 4: df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 3]
    if cols_count >= 5: df["ស្ថានភាព"] = raw_df.iloc[:, 4]

# សម្អាតទិន្នន័យដែលខូច ឬជួរឈរ HTML ចេញ
if not df.empty:
    df = df.dropna(subset=["កូដកាត"])
    df = df[~df["កូដកាត"].astype(str).str.contains("<DIV|<SPAN|html|none", case=False, na=True)]
    df["កូដកាត"] = df["កូដកាត"].astype(str).str.strip().str.upper()

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជន (បូកពិន្ទុ) ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ KR001):", key="verify_input").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    if input_code:
        if not df.empty:
            valid_rows = df[df["កូដកាត"] == input_code]
            
            if not valid_rows.empty:
                idx = valid_rows.index[-1] # ចាប់យកទិន្នន័យចុងក្រោយបង្អស់
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
                        st.warning("💡 បុកលុយចូលប្រព័ន្ធរួចរាល់! សូមធ្វើការ Refresh (F5) កម្មវិធីឡើងវិញ ដើម្បីទាញទិន្នន័យថ្មីមកបង្ហាញក្នុងតារាង។")
                    else:
                        st.error("❌ មានបញ្ហាក្នុងការរក្សាទុកទិន្នន័យ! សូមពិនិត្យមើលលេខ Entry IDs ឡើងវិញ។")
            else:
                st.error(f"❌ មិនមានលេខកូដ {input_code} នេះក្នុងប្រព័ន្ធទេ!")
        else:
            st.error("❌ ប្រព័ន្ធទិន្នន័យទទេរ! សូមបង្កើតកូដថ្មីសាកល្បងខាងក្រោមជាមុនសិន។")
    else:
        st.warning("⚠️ សូមបំពេញលេខកូដកាតជាមុនសិន។")

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
        if not df.empty:
            if new_code in df["កូដកាត"].values:
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
                st.info("💡 បង្កើតកូដជោគជ័យ! សូមធ្វើការ Refresh (F5) កម្មវិធី ដើម្បីឱ្យទិន្នន័យបង្ហាញក្នុងតារាង។")
            else:
                st.error("❌ មិនអាចបញ្ជូនទិន្នន័យទៅកាន់ Google Sheets បានទេ!")
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យរួម ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")

if not df.empty:
    # លុបជួរជាន់គ្នា បង្ហាញតែបច្ចុប្បន្នភាពចុងក្រោយបង្អស់របស់កូដនីមួយៗ
    display_df = df.drop_duplicates(subset=["កូដកាត"], keep="last")
    
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
