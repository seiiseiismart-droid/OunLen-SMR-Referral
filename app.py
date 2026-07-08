import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# ----------------------------------------------------------------
# 🔗 ព័ត៌មានភ្ជាប់ទៅកាន់ Google Form (បានរៀបចំរួចជាស្រេច)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScvhuVjcIYkX61RDDYvu3UuYNoHiQORJuhH5Tb1yL2CWEjUsw/formResponse"

ENTRY_CODE = "entry.236683526"      # លេខសម្រាប់ 'កូដកាត'
ENTRY_NAME = "entry.1741541315"    # លេខសម្រាប់ 'ឈ្មោះម្ចាស់កូដ'
ENTRY_COUNT = "entry.1593503525"   # លេខសម្រាប់ 'ចំនូនអ្នកណែនាំ'
ENTRY_STATUS = "entry.1444218765"  # លេខសម្រាប់ 'ស្ថានភាព'
# ----------------------------------------------------------------

# 1. អានទិន្នន័យ Live ពី Google Sheets (លីងដែលអ្នកបានដាក់ក្នុង Secrets)
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

# សម្អាតឈ្មោះ Column ឱ្យត្រូវគ្នា
df.columns = [str(col).strip() for col in df.columns]

# ដក Column ពេលវេលាចេញ (បើផ្ដើមចេញពី Google Form វានឹងមានទិន្នន័យនេះនៅជួរទី១)
if "Timestamp" in df.columns:
    df = df.drop(columns=["Timestamp"])

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជនថ្មី ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ KR001):").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    if "កូដកាត" in df.columns and input_code in df["កូដកាត"].values:
        # ទាញយកជួរទិន្នន័យចុងក្រោយបង្អស់នៃកូដនោះ
        matching_rows = df[df["កូដកាត"] == input_code]
        idx = matching_rows.index[-1] 
        
        status = str(df.loc[idx, "ស្ថានភាព"]).strip()
        if status == "បានប្រើរួច (Used)":
            st.error(f"❌ កូដ {input_code} នេះត្រូវបានប្រើប្រាស់ និងបើកកាដូរួចរាល់ហើយ!")
        else:
            try:
                current_count = int(df.loc[idx, "ចំនូនអ្នកណែនាំ"]) + 1
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
                st.rerun()
            else:
                st.error("❌ មានបញ្ហាក្នុងការរក្សាទុកទិន្នន័យត្រឡប់ទៅ Sheets!")
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
        if "កូដកាត" in df.columns and new_code in df["កូដកាត"].values:
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
                st.rerun()
            else:
                st.error("❌ មិនអាចបញ្ជូនទិន្នន័យទៅកាន់ Google Sheets បានទេ!")
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យរួម ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")
if not df.empty:
    # ករណីមានកូដដដែលៗ ចាប់យកតែទិន្នន័យចុងក្រោយបង្អស់មកបង្ហាញដើម្បីកុំឱ្យជាន់គ្នា
    display_df = df.drop_duplicates(subset=["កូដកាត"], keep="last")
    if "ចំនូនអ្នកណែនាំ" in display_df.columns:
        display_df["ភាគរយបញ្ចុះតម្លៃសន្សំបាន"] = display_df["ចំនូនអ្នកណែនាំ"].apply(lambda x: f"{int(x) * 10}%" if int(x) < 10 else "FREE 1 ដង")
    st.dataframe(display_df, use_container_width=True)
else:
    st.write("📭 មិនទាន់មានទិន្នន័យអតិថិជននៅឡើយទេ។")
