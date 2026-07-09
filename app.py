import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# ----------------------------------------------------------------
# 🔗 ភ្ជាប់ទៅកាន់ Google Sheets របស់បងដោយផ្ទាល់ (កែសម្រួលទម្រង់ស្វ័យប្រវត្ត)
# ----------------------------------------------------------------
try:
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    if "docs.google.com/spreadsheets" in spreadsheet_url:
        spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
        # ទាញយកទិន្នន័យពីផ្ទាំងឈ្មោះ "Referral" ផ្អែកតាម Sheets របស់បង
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Referral"
    else:
        csv_url = spreadsheet_url

    raw_df = pd.read_csv(csv_url)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីងក្នុង Secrets ឡើងវិញ។")
    st.stop()

# បង្កើតរចនាសម្ព័ន្ធតារាងឱ្យត្រូវ ១០០% តាមរូបភាព Sheets របស់បង
df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព"])

if raw_df is not None and not raw_df.empty:
    raw_df.columns = [str(col).strip() for col in raw_df.columns]
    cols_count = len(raw_df.columns)
    if cols_count >= 1: df["កូដកាត"] = raw_df.iloc[:, 0]
    if cols_count >= 2: df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 1]
    if cols_count >= 3: df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 2]
    if cols_count >= 4: df["ស្ថានភាព"] = raw_df.iloc[:, 3]

# សម្អាតទិន្នន័យដែលទទេរ
if not df.empty:
    df = df.dropna(subset=["កូដកាត"])
    df["កូដកាត"] = df["កូដកាត"].astype(str).str.strip().str.upper()

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជន (បូកពិន្ទុ) ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ 10231010):", key="verify_input").strip().upper()

if st.button("ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary"):
    if input_code:
        if not df.empty:
            valid_rows = df[df["កូដកាត"] == input_code]
            if not valid_rows.empty:
                idx = valid_rows.index[-1]
                status = str(df.loc[idx, "ស្ថានភាព"]).strip()
                
                if status == "បានប្រើរួច (Used)":
                    st.error(f"❌ កូដ {input_code} នេះត្រូវបានប្រើប្រាស់រួចរាល់ហើយ!")
                else:
                    try:
                        current_count = int(float(df.loc[idx, "ចំនំនួនអ្នកណែនាំ"])) + 1
                    except:
                        current_count = 1
                        
                    owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                    new_status = "គ្រប់លក្ខខណ្ឌ (Free)" if current_count >= 10 else "សកម្ម"
                    
                    # 💡 របៀបផ្ញើរក្សាទុកត្រង់ទៅ Sheets តាម Google Forms API Webhook ជំនួសវិញ
                    st.success(f"✅ បានរកឃើញកូដរបស់៖ **{owner_name}**")
                    st.info(f"📈 ចំនួនអ្នកណែនាំបច្ចុប្បន្ន៖ **{current_count} នាក់**")
                    st.warning("⚠️ ប្រព័ន្ធត្រូវការ Google Form ដើម្បីបញ្ជូនទិន្នន័យត្រឡប់ទៅ Sheets វិញ។")
            else:
                st.error(f"❌ មិនមានលេខកូដ {input_code} នេះក្នុងប្រព័ន្ធទេ!")
        else:
            st.error("❌ មិនទាន់មានទិន្នន័យក្នុងប្រព័ន្ធទេ!")
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
            # 💡 ដោយសារបងចង់ចុះឈ្មោះតាមវេបសាយ វិធីដែលលឿនបំផុតគឺបង្កើត Google Form មួយភ្ជាប់នឹង Sheets នេះ
            st.info("ℹ️ ដើម្បីឱ្យទិន្នន័យចុះឈ្មោះរត់ចូលតារាងរបស់បងបាន សូមបងបង្កើត Google Form មួយចេញពី Sheets នេះ។")
            st.markdown("""
            **របៀបបង្កើត Google Form ចេញពី Sheets នេះងាយៗ៖**
            1. នៅក្នុងផ្ទាំង Google Sheets របស់បង ចុចលើម៉ឺនុយ **Tools (ឧបករណ៍)** ខាងលើ។
            2. ជ្រើសរើសយកពាក្យ **Create a new form (បង្កើតទម្រង់ថ្មី)**។
            3. វានឹងបង្កើត Form មួយដែលមានសំណួរត្រូវតាមជួរឈររបស់បងអូតូ រួចផ្ញើលីង Form នោះមកឱ្យខ្ញុំ ខ្ញុំនឹងភ្ជាប់វាឱ្យដើរភ្លាមតែម្ដងបាទ!
            """)
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
