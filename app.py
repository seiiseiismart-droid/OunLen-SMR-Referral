import streamlit as st
import pandas as pd
import requests
import re

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# ----------------------------------------------------------------
# 🔗 ព័ត៌មាន Google Form របស់បង
BASE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeouu-gM5zM0S282gAGaHnUUcF8PRcqQ99zB-rnAaV1hqe-yg"
FORM_RESPONSE_URL = f"{BASE_FORM_URL}/formResponse"
# ----------------------------------------------------------------

# 🔄 អនុវត្តមុខងារទាញយក Entry IDs ដោយស្វ័យប្រវត្តពី HTML របស់ Form
@st.cache_data(ttl="60m")
def get_form_entry_ids(form_url):
    try:
        response = requests.get(form_url)
        if response.status_code == 200:
            # ស្វែងរកលេខកូដ entry.xxxxxxxxx ទាំងអស់នៅក្នុងទំព័រ Form
            matches = re.findall(r'\[(\d+),\[\[\d+,', response.text)
            if not matches:
                # វិធីសាស្ត្រជំនួស បើរកតាមទម្រង់ខាងលើមិនឃើញ
                matches = re.findall(r'name="entry\.(\d+)"', response.text)
            
            # បម្លែងជាបញី្ចគ្រាប់លេខតែម្ដង
            entries = [f"entry.{m}" for m in matches]
            # លុបលេខដែលជាន់គ្នា ចេញ
            unique_entries = list(dict.fromkeys(entries))
            return unique_entries
    except:
        pass
    return []

# ចាប់យក Entry IDs ពី Form ដោយស្វ័យប្រវត្ត
entry_list = get_form_entry_ids(BASE_FORM_URL)

# បើរកមិនឃើញតាមអូតូទេ គឺប្រើលេខបម្រុងដែលជិតត្រូវបំផុត
if len(entry_list) < 4:
    ENTRY_CODE = "entry.170669695"
    ENTRY_NAME = "entry.1561081512"
    ENTRY_COUNT = "entry.687483017"
    ENTRY_STATUS = "entry.1802927231"
else:
    ENTRY_CODE = entry_list[0]
    ENTRY_NAME = entry_list[1]
    ENTRY_COUNT = entry_list[2]
    ENTRY_STATUS = entry_list[3]

# 1. អានទិន្នន័យ Live ពី Google Sheets តាមរយៈលីង CSV ផ្ទាល់
try:
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    if "docs.google.com/spreadsheets" in spreadsheet_url:
        spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
        # ទាញទិន្នន័យពីផ្ទាំងឈ្មោះ "Referral"
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Referral"
    else:
        csv_url = spreadsheet_url

    raw_df = pd.read_csv(csv_url)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីងក្នុង Secrets ឡើងវិញ។")
    st.stop()

# បង្កើតរចនាសម្ព័ន្ធតារាងឱ្យត្រូវ ១០០% ជាមួយ Sheets របស់បង
df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព"])

if raw_df is not None and not raw_df.empty:
    raw_df.columns = [str(col).strip() for col in raw_df.columns]
    cols_count = len(raw_df.columns)
    
    # ករណីមានជួរឈរ Timestamp នៅខាងមុខ (សរុបមាន ៥ ជួរឈរ)
    if cols_count >= 5:
        df["កូដកាត"] = raw_df.iloc[:, 1]
        df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 2]
        df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 3]
        df["ស្ថានភាព"] = raw_df.iloc[:, 4]
    # ករណីអត់មានជួរឈរ Timestamp ទេ (សរុបមាន ៤ ជួរឈរ)
    elif cols_count >= 4:
        df["កូដកាត"] = raw_df.iloc[:, 0]
        df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 1]
        df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 2]
        df["ស្ថានភាព"] = raw_df.iloc[:, 3]

# សម្អាតទិន្នន័យ
if not df.empty:
    df = df.dropna(subset=["កូដកាត"])
    df = df[~df["កូដកាត"].astype(str).str.contains("<DIV|<SPAN|html|none", case=False, na=True)]
    df["កូដកាត"] = df["កូដកាត"].astype(str).str.strip().str.upper()

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជន (បូកពិន្ទុ) ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ 10231010):", key="verify_input").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    if input_code:
        if not df.empty and df["កូដកាត"].notnull().any():
            valid_rows = df[df["កូដកាត"] == input_code]
            
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
                    
                    response = requests.post(FORM_RESPONSE_URL, data=form_data)
                    
                    if response.status_code == 200 or "closed" not in response.text.lower():
                        st.success(f"✅ បានរកឃើញកូដរបស់៖ **{owner_name}**")
                        st.info(f"📈 ចំនួនអ្នកណែនាំបច្ចុប្បន្ន៖ **{current_count} នាក់** (ទទួលបានការបញ្ចុះតម្លៃ {current_count * 10}%)")
                        if current_count >= 10:
                            st.balloons()
                        st.warning("💡 បូកពិន្ទុចូលប្រព័ន្ធរួចរាល់! សូមធ្វើការ Refresh (F5) កម្មវិធីឡើងវិញ ដើម្បីទាញទិន្នន័យថ្មីមកបង្ហាញ។")
                    else:
                        st.error("❌ មានបញ្ហាក្នុងការរក្សាទុកទិន្នន័យ! សូមពិនិត្យមើលសិទ្ធិបើកទទួលចម្លើយរបស់ Form។")
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
    new_code = st.text_input("បង្កើតលេខកូដថ្មី (ឧទាហរណ៍៖ 10231010):", key="new_code_input").strip().upper()
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
            response = requests.post(FORM_RESPONSE_URL, data=form_data)
            
            # បើផ្ញើជោគជ័យ (Status 200 ឬ ទំព័រ Form មិនបានបិទចម្លើយ)
            if response.status_code == 200 or "closed" not in response.text.lower():
                st.success(f"🎉 ចុះឈ្មោះកូដ {new_code} ជូនលោក/លោកស្រី {new_name} ជោគជ័យ!")
                st.balloons()
                st.info("💡 បង្កើតកូដជោគជ័យ! សូមធ្វើការ Refresh (F5) កម្មវិធី ដើម្បីឱ្យទិន្នន័យបង្ហាញក្នុងតារាង។")
            else:
                st.error("❌ មិនអាចបញ្ជូនទិន្នន័យទៅកាន់ Google Sheets បានទេ! សូមប្រាកដថា Form របស់បងបានបើកសិទ្ធិទទួលចម្លើយ (Accepting responses)។")
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យរួម ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")

if not df.empty:
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
