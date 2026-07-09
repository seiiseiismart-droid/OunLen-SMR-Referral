import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងពិនិត្យការបញ្ចុះតម្លៃ")

# ----------------------------------------------------------------
# 🔗 ទាញយកព័ត៌មានលីងពី Secrets
# ----------------------------------------------------------------
try:
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    SCRIPT_URL = st.secrets["connections"]["gsheets"]["script_url"]
    
    if "docs.google.com/spreadsheets" in spreadsheet_url:
        spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Referral"
    else:
        csv_url = spreadsheet_url

    raw_df = pd.read_csv(csv_url)
except Exception as e:
    st.error("❌ មិនអាចភ្ជាប់ទៅកាន់ Google Sheets បានទេ! សូមពិនិត្យមើលលីងក្នុង Secrets ឡើងវិញ។")
    st.stop()

# រៀបចំរចនាសម្ព័ន្ធតារាងអាន (Timestamp, កូដកាត, ឈ្មោះម្ចាស់កូដ, ចំនំនួនអ្នកណែនាំ, រូបភាព, ស្ថានភាព)
df = pd.DataFrame(columns=["កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "រូបភាព", "ស្ថានភាព"])

if raw_df is not None and not raw_df.empty:
    raw_df.columns = [str(col).strip() for col in raw_df.columns]
    cols_count = len(raw_df.columns)
    
    if cols_count >= 6: 
        df["កូដកាត"] = raw_df.iloc[:, 1]
        df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 2]
        df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 3]
        df["រូបភាព"] = raw_df.iloc[:, 4]
        df["ស្ថានភាព"] = raw_df.iloc[:, 5]
    elif cols_count >= 5:
        df["កូដកាត"] = raw_df.iloc[:, 1]
        df["ឈ្មោះម្ចាស់កូដ"] = raw_df.iloc[:, 2]
        df["ចំនំនួនអ្នកណែនាំ"] = raw_df.iloc[:, 3]
        df["ស្ថានភាព"] = raw_df.iloc[:, 4]
        df["រូបភាព"] = ""

if not df.empty:
    df = df.dropna(subset=["កូដកាត"])
    df["កូដកាត"] = df["កូដកាត"].astype(str).str.strip().str.upper()

st.markdown("---")

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជន (បូកពិន្ទុ និង Reset ពិន្ទុ) ---
st.header("📥 ទទួលកូដពីអតិថិជន")
input_code = st.text_input("វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ 10231010):", key="verify_input").strip().upper()

# បង្កើតឡៅតឿប៊ូតុងជា ៣ ជួរឈរ
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    verify_clicked = st.button("➕ ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ", type="primary", use_container_width=True)

with btn_col2:
    view_photo_clicked = st.button("👁️ មើលរូបថតអតិថិជន", use_container_width=True)

with btn_col3:
    reset_clicked = st.button("🔄 ប្រើប្រាស់ការបញ្ចុះតម្លៃ (Reset ពិន្ទុ)", use_container_width=True)

# ករណីចុចប៊ូតុង "មើលរូបថត"
if view_photo_clicked:
    if input_code:
        if not df.empty:
            valid_rows = df[df["កូដកាត"] == input_code]
            if not valid_rows.empty:
                idx = valid_rows.index[-1]
                owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                img_url = df.loc[idx, "រូបភាព"]
                
                st.info(f"👤 អតិថិជនឈ្មោះ៖ **{owner_name}**")
                if img_url and str(img_url).startswith("http"):
                    st.image(img_url, caption=f"រូបថតរបស់ {owner_name}", width=300)
                else:
                    st.warning("⚠️ អតិថិជនម្នាក់នេះមិនទាន់មានរូបថតនៅក្នុងប្រព័ន្ធនៅឡើយទេ។")
            else:
                st.error(f"❌ មិនមានលេខកូដ {input_code} នេះក្នុងប្រព័ន្ធទេ!")
        else:
            st.error("❌ មិនទាន់មានទិន្នន័យនៅក្នុងតារាងទេ!")
    else:
        st.warning("⚠️ សូមបំពេញលេខកូដកាតដែលចង់មើលរូបថតជាមុនសិន។")

# ករណីចុចប៊ូតុង "🔄 ប្រើប្រាស់ការបញ្ចុះតម្លៃ (Reset ពិន្ទុ)"
if reset_clicked:
    if input_code:
        if not df.empty:
            valid_rows = df[df["កូដកាត"] == input_code]
            if not valid_rows.empty:
                idx = valid_rows.index[-1]
                owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                img_url = df.loc[idx, "រូបភាព"]
                
                # កំណត់ពិន្ទុទៅ ០ និងស្ថានភាពទៅ "សកម្ម" ឡើងវិញ ដើម្បីឱ្យគាត់សន្សំសារជាថ្មី
                params = {
                    "action": "update",
                    "code": input_code,
                    "name": owner_name,
                    "count": 0,
                    "status": "សកម្ម",
                    "image": img_url
                }
                response = requests.post(SCRIPT_URL, params=params)
                
                if response.status_code == 200:
                    st.success(f"🎉 បានប្រើប្រាស់ការបញ្ចុះតម្លៃរួចរាល់! កូដរបស់ **{owner_name}** ត្រូវបាន Reset ទៅ ០ នាក់វិញហើយ។")
                    st.info("📈 អតិថិជនអាចចាប់ផ្ដើមសន្សំពិន្ទុភាគរយបញ្ចុះតម្លៃសារជាថ្មីម្តងទៀតបានបាទ។")
                    st.balloons()
                else:
                    st.error("❌ មិនអាចកែប្រែទិន្នន័យបានទេ!")
            else:
                st.error(f"❌ មិនមានលេខកូដ {input_code} នេះក្នុងប្រព័ន្ធទេ!")
        else:
            st.error("❌ មិនទាន់មានទិន្នន័យនៅក្នុងតារាងទេ!")
    else:
        st.warning("⚠️ សូមបំពេញលេខកូដកាតជាមុនសិន។")

# ករណីចុចប៊ូតុង "ផ្ទៀងផ្ទាត់ និងបូកពិន្ទុ"
if verify_clicked:
    if input_code:
        if not df.empty:
            valid_rows = df[df["កូដកាត"] == input_code]
            
            if not valid_rows.empty:
                idx = valid_rows.index[-1]
                status = str(df.loc[idx, "ស្ថានភាព"]).strip()
                
                try:
                    current_count = int(float(df.loc[idx, "ចំនំនួនអ្នកណែនាំ"])) + 1
                except:
                    current_count = 1
                    
                owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                img_url = df.loc[idx, "រូបភាព"]
                new_status = "គ្រប់លក្ខខណ្ឌ (Free)" if current_count >= 10 else "សកម្ម"
                
                if img_url and str(img_url).startswith("http"):
                    st.image(img_url, caption=f"រូបថតរបស់ {owner_name}", width=150)
                
                params = {
                    "action": "update",
                    "code": input_code,
                    "name": owner_name,
                    "count": current_count,
                    "status": new_status,
                    "image": img_url
                }
                response = requests.post(SCRIPT_URL, params=params)
                
                if response.status_code == 200:
                    st.success(f"✅ បានបូកពិន្ទុជូនកូដរបស់៖ **{owner_name}** ជោគជ័យ!")
                    st.info(f"📈 ចំនួនអ្នកណែនាំបច្ចុប្បន្ន៖ **{current_count} នាក់** (បញ្ចុះតម្លៃ {current_count * 10}%)")
                    if current_count >= 10: 
                        st.balloons()
                        st.warning("🎉 អតិថិជនម្នាក់នេះសន្សំគ្រប់ ១០ នាក់ហើយ! គាត់ទទួលបានការធ្វើសក់ 🆓 Free 1 ដង។ បន្ទាប់ពីធ្វើជូនគាត់រួច សូមកុំភ្លេចចុចប៊ូតុង Reset ខាងលើបាទ!")
                else:
                    st.error("❌ មិនអាចរក្សាទុកទិន្នន័យបានទេ!")
            else:
                st.error(f"❌ មិនមានលេខកូដ {input_code} នេះក្នុងប្រព័ន្ធទេ!")
        else:
            st.error("❌ មិនទាន់មានទិន្នន័យនៅក្នុងតារាងទេ!")
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

# 📸 បង្កើតប៊ូតុងសម្រាប់ បើក/បិទ កាមេរ៉ា
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False

if st.button("📸 បើក / បិទ កាមេរ៉ាថតរូប"):
    st.session_state.show_camera = not st.session_state.show_camera

camera_photo = None
if st.session_state.show_camera:
    st.write("📷 កាមេរ៉ារួចរាល់៖")
    camera_photo = st.camera_input("ចុច Take Photo ដើម្បីថតរូបអតិថិជន")

def upload_image_to_cloud(file):
    try:
        api_key = "6d207e02198a847aa98d0a2a901485a5" 
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": api_key}
        files = {"image": file.getvalue()}
        res = requests.post(url, data=payload, files=files)
        return res.json()["data"]["url"]
    except:
        return ""

if st.button("ចុះឈ្មោះកូដថ្មី"):
    if new_code and new_name:
        is_duplicate = False
        if not df.empty:
            if new_code in df["កូដកាត"].values: is_duplicate = True
                
        if is_duplicate:
            st.error("❌ លេខកូដនេះមានរួចហើយ!")
        else:
            final_img_url = ""
            if camera_photo is not None:
                with st.spinner("⏳ កំពុងរក្សាទុករូបថតចូលក្នុងប្រព័ន្ធ..."):
                    final_img_url = upload_image_to_cloud(camera_photo)
            
            params = {
                "action": "create",
                "code": new_code,
                "name": new_name,
                "image": final_img_url
            }
            response = requests.post(SCRIPT_URL, params=params)
            
            if response.status_code == 200:
                st.success(f"🎉 ចុះឈ្មោះកូដ {new_code} ជូនលោក/លោកស្រី {new_name} ជោគជ័យ!")
                st.session_state.show_camera = False
                st.balloons()
            else:
                st.error("❌ មិនអាចចុះឈ្មោះបានទេ!")
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
    
    final_cols = ["រូបភាព", "កូដកាត", "ឈ្មោះម្ចាស់កូដ", "ចំនំនួនអ្នកណែនាំ", "ស្ថានភាព", "ភាគរយបញ្ចុះតម្លៃសន្សំបាន"]
    display_df["រូបភាព"] = display_df["រូបភាព"].apply(lambda x: x if (isinstance(x, str) and x.startswith("http")) else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
    
    st.data_editor(
        display_df[final_cols].reset_index(drop=True),
        column_config={
            "រូបភាព": st.column_config.ImageColumn("រូបថត", help="រូបថតអតិថិជន", width="small")
        },
        disabled=True,
        use_container_width=True
    )
else:
    st.info("📭 មិនទាន់មានទិន្នន័យអតិថិជននៅក្នុងប្រព័ន្ធឡើយ។ 🥰")
