import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# 🔗 បង្កើតការតភ្ជាប់ត្រង់ទៅកាន់ Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # អានទិន្នន័យពី Sheet ឈ្មោះ "Form_Responses" (ផ្អែកតាមរូបភាពសន្លឹកកិច្ចការរបស់បង)
    df = conn.read(worksheet="Form_Responses", ttl="0m")
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលការកំណត់ក្នុង Secrets ឡើងវិញ។")
    st.stop()

# សម្អាតឈ្មោះ Column ឱ្យស្អាត
df.columns = [str(col).strip() for col in df.columns]

# បើមិនទាន់មាន Column ទាំងនេះទេ គឺបង្កើតឱ្យវាមានសិន ការពារកំហុសកូដ
required_cols = ["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព"]
for col in required_cols:
    if col not in df.columns:
        df[col] = None

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជនថ្មី (បូកពិន្ទុ) ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ KR001):", key="verify_input").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    if input_code:
        # សម្អាតទិន្នន័យដើម្បីផ្ទៀងផ្ទាត់
        df["កូដកាត_clean"] = df["កូដកាត"].astype(str).str.strip().str.upper()
        valid_rows = df[df["កូដកាត_clean"] == input_code]
        
        if not valid_rows.empty:
            idx = valid_rows.index[-1] # ចាប់យកជួរចុងក្រោយ
            
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
                
                # កែប្រែទិន្នន័យក្នុង DataFrame
                df.loc[idx, "ចំនំនួនអ្នកណែនាំ"] = current_count
                df.loc[idx, "ស្ថានភាព"] = new_status
                
                # លុប Column បណ្ដោះអាសន្នចេញមុននឹង Save ទៅ Sheets
                if "កូដកាត_clean" in df.columns:
                    df = df.drop(columns=["កូដកាត_clean"])
                
                # រក្សាទុកត្រឡប់ទៅ Google Sheets ផ្ទាល់តែម្ដង
                conn.update(worksheet="Form_Responses", data=df)
                
                st.success(f"✅ បានរកឃើញកូដរបស់៖ **{owner_name}**")
                st.info(f"📈 ចំនួនអ្នកណែនាំបច្ចុប្បន្ន៖ **{current_count} នាក់** (ទទួលបានការបញ្ចុះតម្លៃ {current_count * 10}%)")
                if current_count >= 10:
                    st.balloons()
                    st.warning(f"🎉 ម្ចាស់កូដ **{owner_name}** ណែនាំគ្រប់ ១០នាក់ហើយ! ទទួលបានសេវាកម្មហ្វ្រី ១ដង។")
                st.rerun()
        else:
            st.error(f"❌ មិនមានលេខកូដ {input_code} នេះក្នុងប្រព័ន្ធទេ!")
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
        df["កូដកាត_str"] = df["កូដកាត"].astype(str).str.strip().str.upper()
        
        if new_code in df["កូដកាត_str"].values:
            st.error("❌ លេខកូដនេះមានរួចហើយ!")
        else:
            # បង្កើតជួរទិន្នន័យថ្មី
            new_row = {
                "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "កូដកាត": new_code,
                "ឈ្មោះម្ចាស់កូដ": new_name,
                "ចំនំនួនអ្នកណែនាំ": 0,
                "ស្ថានភាព": "សកម្ម"
            }
            
            # បន្ថែមចូលតារាង
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # លុប Column បណ្ដោះអាសន្នចេញមុននឹង Save
            if "កូដកាត_str" in df.columns:
                df = df.drop(columns=["កូដកាត_str"])
            if "កូដកាត_clean" in df.columns:
                df = df.drop(columns=["កូដកាត_clean"])
                
            # រក្សាទុកត្រឡប់ទៅ Google Sheets
            conn.update(worksheet="Form_Responses", data=df)
            
            st.success(f"🎉 ចុះឈ្មោះកូដ {new_code} ជូនលោក/លោកស្រី {new_name} ជោគជ័យ!")
            st.balloons()
            st.rerun()
    else:
        st.warning("⚠️ សូមបំពេញទាំងលេខកូដ និងឈ្មោះអតិថិជន។")

st.markdown("---")

# --- ផ្នែកទី ៣៖ បង្ហាញទិន្នន័យរួម ---
st.header("📊 តារាងតាមដានទិន្នន័យរួម (Live)")

# លុបជួរឈរដែលមិនចាំបាច់ចេញមុនបង្ហាញ
display_df = df.copy()
if "កូដកាត_clean" in display_df.columns:
    display_df = display_df.drop(columns=["កូដកាត_clean"])
if "កូដកាត_str" in display_df.columns:
    display_df = display_df.drop(columns=["កូដកាត_str"])

# បង្ហាញតែជួរណាដែលមានទិន្នន័យកូដកាតពិតប្រាកដ
display_df = display_df.dropna(subset=["កូដកាត"])
display_df = display_df[display_df["កូដកាត"].astype(str).str.strip() != ""]

if not display_df.empty:
    def calculate_discount(x):
        try:
            val = int(float(x))
            return f"{val * 10}%" if val < 10 else "FREE 1 ដង"
        except:
            return "0%"
            
    display_df["ភាគរយបញ្ចុះតម្លៃសន្សំបាន"] = display_df["ចំនំនួនអ្នកណែនាំ"].apply(calculate_discount)
    
    # រៀបចំលំដាប់លំដោយ Columns ឱ្យស្អាត
    cols_to_show = ["Timestamp", "កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព", "ភាគរយបញ្ចុះតម្លៃសន្សំបាន"]
    # បើអត់ទាន់មានជួរ Timestamp ទេ មិនបាច់បង្ហាញទេ
    cols_to_show = [c for c in cols_to_show if c in display_df.columns]
    
    st.dataframe(display_df[cols_to_show].reset_index(drop=True), use_container_width=True)
else:
    st.info("📭 មិនទាន់មានទិន្នន័យអតិថិជននៅក្នុងប្រព័ន្ធឡើយ។ សាកល្បងបង្កើតកូដថ្មីខាងលើ! 🥰")
