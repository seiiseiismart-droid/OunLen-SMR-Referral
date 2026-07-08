import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# ភ្ជាប់ទៅកាន់ Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីងក្នុង Secrets ឡើងវិញ។")
    st.info(f"ព័ត៌មានកំហុស៖ {e}")
    st.stop()

# បង្កើតទម្រង់លំនាំដើមបើទិន្នន័យទទេរ
if df is None or df.empty:
    df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនួនអ្នកណែនាំ", "ស្ថានភាព"])

# សម្អាតឈ្មោះ Column ឱ្យត្រូវស្តង់ដារ
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
            st.error(f"❌ កូដ {input_code} នេះត្រូវបានប្រើប្រាស់រួចហើយ!")
        else:
            try:
                current_count = int(df.loc[idx, "ចំនួនអ្នកណែនាំ"]) + 1
            except:
                current_count = 1
                
            df.loc[idx, "ចំនួនអ្នកណែនាំ"] = current_count
            owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
            
            if current_count >= 10:
                st.balloons()
                df.loc[idx, "ស្ថានភាព"] = "គ្រប់លក្ខខណ្ឌ (Free)"
            
            # រក្សាទុកត្រឡប់ទៅ Sheets វិញ
            conn.update(data=df)
            st.success(f"✅ បូកពិន្ទុជូន៖ **{owner_name}** ជោគជ័យ! (សរុប៖ {current_count} នាក់)")
            st.rerun()
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
            new_row = pd.DataFrame([{"កូដកាត": new_code, "ឈ្មោះម្ចាស់កូដ": new_name, "ចំនួនអ្នកណែនាំ": 0, "ស្ថានភាព": "សកម្ម"}])
            df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=df)
            st.success(f"🎉 ចុះឈ្មោះកូដ {new_code} ជូនលោក/លោកស្រី {new_name} ជោគជ័យ!")
            st.rerun()
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យរួម ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")
if not df.empty:
    display_df = df.copy()
    if "ចំនួនអ្នកណែនាំ" in display_df.columns:
        display_df["ភាគរយបញ្ចុះតម្លៃសន្សំបាន"] = display_df["ចំនួនអ្នកណែនាំ"].apply(lambda x: f"{int(x) * 10}%" if int(x) < 10 else "FREE 1 ដង")
    st.dataframe(display_df, use_container_width=True)
else:
    st.write("📭 មិនទាន់មានទិន្នន័យអតិថិជននៅឡើយទេ។")
