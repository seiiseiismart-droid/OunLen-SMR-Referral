import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# 1. ទាញយក URL របស់ Google Sheets ពី Secrets
try:
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # ភ្ជាប់ទៅកាន់ Google Sheets តាមរយៈ gspread (Public Link Mode)
    gc = gspread.public()
    # បើកសន្លឹកកិច្ចការ
    sh = gc.open_by_url(sheet_url)
    
    # ព្យាយាមបើកសន្លឹក "Referrals" បើមិនមានទេ ឱ្យបើកសន្លឹកដំបូងគេ
    try:
        worksheet = sh.worksheet("Referrals")
    except:
        try:
            worksheet = sh.worksheet("Referral")
        except:
            worksheet = sh.get_worksheet(0)
            
    # អានទិន្នន័យមកជា DataFrame
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីង ឬទំហំផ្ទុកអ៊ីមែលរបស់អ្នក។")
    st.info(f"ព័ត៌មានលម្អិតនៃកំហុស: {e}")
    st.stop()

# ករណីទិន្នន័យទទេរ ឱ្យបង្កើតទម្រង់លំនាំដើម
if df.empty:
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
        # ជួរឈរនៅក្នុង Google Sheets (គិតចាប់ពីជួរទី ២ ព្រោះជួរទី១ ជា Header)
        row_num = int(idx) + 2
        
        status = str(df.loc[idx, "ស្ថានភាព"]).strip()
        if status == "បានប្រើរួច (Used)":
            st.error(f"❌ កូដ {input_code} នេះត្រូវបានប្រើប្រាស់ និងបើកកាដូរួចរាល់ហើយ!")
        else:
            try:
                current_count = int(df.loc[idx, "ចំនួនអ្នកណែនាំ"]) + 1
            except:
                current_count = 1
                
            owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
            
            # រក្សាទុកតម្លៃថ្មីទៅ Google Sheets ដោយផ្ទាល់ទៅលើ Cell នីមួយៗ
            # រកជួរឈរ (Column)
            col_count_idx = df.columns.get_loc("ចំនួនអ្នកណែនាំ") + 1
            col_status_idx = df.columns.get_loc("ស្ថានភាព") + 1
            
            try:
                worksheet.update_cell(row_num, col_count_idx, current_count)
                
                st.success(f"✅ បានរកឃើញកូដរបស់៖ **{owner_name}**")
                st.info(f"📈 ចំនួនអ្នកណែនាំបច្ចុប្បន្ន៖ **{current_count} នាក់** (ទទួលបានការបញ្ចុះតម្លៃ {current_count * 10}%)")
                
                if current_count >= 10:
                    st.balloons()
                    st.warning(f"🎉 ម្ចាស់កូដ **{owner_name}** ណែនាំគ្រប់ ១០នាក់ហើយ! គាត់ទទួលបាន **សេវាកម្មហ្វ្រី ១ដង** នៅពេលមកលើកក្រោយ។")
                    worksheet.update_cell(row_num, col_status_idx, "គ្រប់លក្ខខណ្ឌ (Free)")
                
                st.success("💾 បានរក្សាទុកទិន្នន័យទៅក្នុងប្រព័ន្ធអនឡាញរួចរាល់!")
                st.rerun()
            except Exception as update_err:
                st.error(f"❌ មិនអាចកែប្រែទិន្នន័យបានទេ៖ {update_err}")
                st.warning("⚠️ អាចមកពី Google Drive របស់អ្នកពេញ (15GB)។ សូមសម្អាតទំហំផ្ទុក Drive របស់អ្នក រួចសាកល្បងឡើងវិញ។")
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
            try:
                # បន្ថែមជួរថ្មីទៅក្នុង Google Sheets ផ្ទាល់តែម្តង
                worksheet.append_row([new_code, new_name, 0, "សកម្ម"])
                st.success(f"🎉 ចុះឈ្មោះកូដ {new_code} ជូនលោក/លោកស្រី {new_name} ជោគជ័យ!")
                st.rerun()
            except Exception as append_err:
                st.error(f"❌ មិនអាចចុះឈ្មោះបានទេ៖ {append_err}")
                st.warning("⚠️ សូមពិនិត្យមើលថាតើ Google Drive របស់អ្នកពេញ (15GB) ដែរឬទេ?")
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
