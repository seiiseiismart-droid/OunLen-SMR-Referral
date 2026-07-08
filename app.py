import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# 1. ទាញយក URL របស់ Google Sheets ពី Secrets រួចបំប្លែងទៅជាទម្រង់ទាញទិន្នន័យ (CSV export URL)
try:
    original_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # បំប្លែងតំណភ្ជាប់ឱ្យទៅជាលីងទាញយកទិន្នន័យ CSV ផ្ទាល់
    if "edit?usp=sharing" in original_url:
        csv_url = original_url.replace("edit?usp=sharing", "gviz/tq?tqx=out:csv")
    elif "edit#" in original_url:
        csv_url = original_url.split("edit#")[0] + "gviz/tq?tqx=out:csv"
    else:
        csv_url = original_url
        
    # អានទិន្នន័យដោយប្រើ Pandas ផ្ទាល់
    df = pd.read_csv(csv_url)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីង ឬការកំណត់ទំហំផ្ទុករបស់អ្នក។")
    st.info(f"ព័ត៌មានលម្អិតនៃកំហុស: {e}")
    st.stop()

# ករណីទិន្នន័យទទេរ ឱ្យបង្កើតទម្រង់លំនាំដើម
if df is None or df.empty:
    df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនួនអ្នកណែនាំ", "ស្ថានភាព"])

# សម្អាតឈ្មោះ Column
df.columns = [str(col).strip() for col in df.columns]

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជនថ្មី ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ KR001):").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    if "កូដកាត" in df.columns and input_code in df["កូដកាត"].values:
        idx = df[df["កូដកាត"] == input_code].index[0]
        
        status = str(df.loc[idx, "ស្ថានភាព"]).strip()
        if status == "បានប្រើរួច (Used)":
            st.error(f"❌ កូដ {input_code} នេះត្រូវបានប្រើប្រាស់ និងបើកកាដូរួចរាល់ហើយ!")
        else:
            try:
                current_count = int(df.loc[idx, "ចំនួនអ្នកណែនាំ"]) + 1
            except:
                current_count = 1
                
            owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
            
            st.success(f"✅ បានរកឃើញកូដរបស់៖ **{owner_name}**")
            st.info(f"📈 ចំនួនអ្នកណែនាំបច្ចុប្បន្ន៖ **{current_count} នាក់** (ទទួលបានការបញ្ចុះតម្លៃ {current_count * 10}%)")
            
            if current_count >= 10:
                st.balloons()
                st.warning(f"🎉 ម្ចាស់កូដ **{owner_name}** ណែនាំគ្រប់ ១០នាក់ហើយ! គាត់ទទួលបាន **សេវាកម្មហ្វ្រី ១ដង** នៅពេលមកលើកក្រោយ។")
            
            # ចំណាំ៖ ដោយសារការប្រើប្រាស់លីងទូទៅ (Public Link) អនុញ្ញាតឱ្យតែអានទិន្នន័យ (Read-only)
            # ដើម្បីអាចកែប្រែទិន្នន័យបាន (Write/Update) អ្នកត្រូវសម្អាតទំហំផ្ទុកអ៊ីមែលរបស់អ្នក (15GB) រួចប្រើប្រាស់ Service Account (JSON Key)។
            st.warning("⚠️ ប្រព័ន្ធបានផ្ទៀងផ្ទាត់ជោគជ័យ ប៉ុន្តែការរក្សាទុកត្រឡប់ទៅ Google Sheets វិញត្រូវបានផ្អាក ដោយសារទំហំផ្ទុក Google Drive របស់អ្នកពេញ។")
    else:
        st.error("❌ មិនមានលេខកូដនេះក្នុងប្រព័ន្ធ ឬតារាង Google Sheets មិនទាន់មានក្បាលជួរឈរឡើយ!")

st.markdown("---")

# --- ផ្នែកទី ២៖ បង្កើតកូដថ្មីសម្រាប់អតិថិជន ---
st.header("➕ បង្កើតកូដថ្មី (សម្រាប់អតិថិជនទើបមកដំបូង)")
col1, col2 = st.columns(2)
with col1:
    new_code = st.text_input("បង្កើតលេខកូដថ្មី (ឧទាហរណ៍៖ KR004):").strip().upper()
with col2:
    new_name = st.text_input("ឈ្មោះអតិថិជន:")

if st.button("ចុះឈ្មោះកូដថ្មី"):
    if new_code and new_name:
        if "កូដកាត" in df.columns and new_code in df["កូដកាត"].values:
            st.error("❌ លេខកូដនេះមានរួចហើយ!")
        else:
            st.info(f"📋 បានកត់ត្រាទិន្នន័យបណ្តោះអាសន្ន៖ {new_code} - {new_name}")
            st.warning("⚠️ មិនទាន់អាចបន្ថែមទៅ Google Sheets បានទេ ដោយសារគណនី Google របស់អ្នកពេញទំហំផ្ទុក (15GB)។ សូមសម្អាត Space ក្នុង Drive របស់អ្នកជាមុនសិន។")
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យសរុបក្នុងហាង ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")
if not df.empty:
    display_df = df.copy()
    if "ចំនួនអ្នកណែនាំ" in display_df.columns:
        display_df["ភាគរយបញ្ចុះតម្លៃសន្សំបាន"] = display_df["ចំនួនអ្នកណែនាំ"].apply(lambda x: f"{int(x) * 10}%" if int(x) < 10 else "FREE 1 ដង")
    st.dataframe(display_df, use_container_width=True)
else:
    st.write("📭 មិនទាន់មានទិន្នន័យអតិថិជននៅឡើយទេ។")
