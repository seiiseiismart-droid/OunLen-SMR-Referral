import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Kongrei Mart - Referral System", page_icon="🇰🇭", layout="centered")

st.title("កង្រី ម៉ាត - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# 1. ភ្ជាប់ទៅកាន់ Google Sheets (សន្លឹកទិន្នន័យអនឡាញ)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # អានទិន្នន័យពី Sheet ឈ្មោះ "Referrals"
    df = conn.read(worksheet="Referrals", ttl="0")
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យការកំណត់ខាងក្រោម។")
    st.stop()

# បំពេញទិន្នន័យបើទទេរ
if df.empty:
    df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនួនអ្នកណែនាំ", "ស្ថានភាព"])

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជនថ្មី ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ KR001):").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    if input_code in df["កូដកាត"].values:
        idx = df[df["កូដកាត"] == input_code].index[0]
        
        if df.loc[idx, "ស្ថានភាព"] == "បានប្រើរួច (Used)":
            st.error(f"❌ កូដ {input_code} នេះត្រូវបានប្រើប្រាស់ និងបើកកាដូរួចរាល់ហើយ!")
        else:
            # បន្ថែមចំនួនអ្នកណែនាំ ១នាក់
            df.loc[idx, "ចំនួនអ្នកណែនាំ"] = int(df.loc[idx, "ចំនួនអ្នកណែនាំ"]) + 1
            current_count = int(df.loc[idx, "ចំនួនអ្នកណែនាំ"])
            owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
            
            st.success(f"✅ បានរកឃើញកូដរបស់៖ **{owner_name}**")
            st.info(f"📈 ចំនួនអ្នកណែនាំបច្ចុប្បន្ន៖ **{current_count} នាក់** (ទទួលបានការបញ្ចុះតម្លៃ {current_count * 10}%)")
            
            if current_count >= 10:
                st.balloons()
                st.warning(f"🎉 ម្ចាស់កូដ **{owner_name}** ណែនាំគ្រប់ ១០នាក់ហើយ! គាត់ទទួលបាន **សេវាកម្មហ្វ្រី ១ដង** នៅពេលមកលើកក្រោយ។")
                df.loc[idx, "ស្ថានភាព"] = "គ្រប់លក្ខខណ្ឌ (Free)"
            
            # រក្សាទុកទិន្នន័យទៅលើ Google Sheets វិញភ្លាមៗ
            conn.update(worksheet="Referrals", data=df)
            st.success("💾 បានរក្សាទុកទិន្នន័យទៅក្នុងប្រព័ន្ធអនឡាញរួចរាល់!")
    else:
        st.error("❌ មិនមានលេខកូដនេះក្នុងប្រព័ន្ធឡើយ! សូមពិនិត្យមើលឡើងវិញ។")

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
        if new_code in df["កូដកាត"].values:
            st.error("❌ លេខកូដនេះមានរួចហើយ!")
        else:
            # បន្ថែមជួរថ្មី
            new_row = pd.DataFrame([{"កូដកាត": new_code, "ឈ្មោះម្ចាស់កូដ": new_name, "ចំនួនអ្នកណែនាំ": 0, "ស្ថានភាព": "សកម្ម"}])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # រក្សាទុកទៅ Google Sheets
            conn.update(worksheet="Referrals", data=df)
            st.success(f"🎉 ចុះឈ្មោះកូដ {new_code} ជូនលោក/លោកស្រី {new_name} ជោគជ័យ!")
            st.rerun()
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យសរុបក្នុងហាង ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")
display_df = df.copy()
if not display_df.empty:
    display_df["ភាគរយបញ្ចុះតម្លៃសន្សំបាន"] = display_df["ចំនួនអ្នកណែនាំ"].apply(lambda x: f"{int(x) * 10}%" if int(x) < 10 else "FREE 1 ដង")
st.dataframe(display_df, use_container_width=True)
