import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="OunLen SMR - Referral System", page_icon="💇‍♀️", layout="centered")

st.title("អូនឡែន សម្រស់ - ប្រព័ន្ធគ្រប់គ្រងកូដណែនាំ 🇰🇭")
st.write("សម្រាប់ម្ចាស់ហាង/បុគ្គលិក៖ វាយបញ្ចូលកូដដើម្បីបន្ថែមពិន្ទុ និងប្រើប្រាស់ការបញ្ចុះតម្លៃ")

# អត្រាប្ដូរប្រាក់ថេរ
EXCHANGE_RATE = 4050

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

# រៀបចំរចនាសម្ព័ន្ធតារាងអាន
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

# --- ផ្នែកទី ១៖ ទទួលកូដពីអតិថិជន ---
st.header("📥 គ្រប់គ្រងកូដអតិថិជន")

input_code = st.text_input("🔍 វាយបញ្ចូលលេខកូដកាត (ឧទាហរណ៍៖ 10231010):", key="verify_input").strip().upper()

# បង្កើតប្រឡោះបញ្ចូលតម្លៃជា ២ ជម្រើស (ដុល្លារ និង រៀល)
st.write("💵 បញ្ចូលតម្លៃសេវាកម្មសរុប (ជ្រើសរើសវាយប្រឡោះណាមួយក៏បាន)៖")
currency_col1, currency_col2 = st.columns(2)

with currency_col1:
    price_usd = st.number_input("តម្លៃជា ដុល្លារ ($)", min_value=0.0, step=0.5, format="%.2f")
with currency_col2:
    price_khr = st.number_input("តម្លៃជា រៀល (៛)", min_value=0, step=500)

# គណនាតម្លៃដើមសរុបជា USD ដើម្បីយកទៅគណនាបន្ត
if price_usd > 0:
    base_price_usd = price_usd
elif price_khr > 0:
    base_price_usd = price_khr / EXCHANGE_RATE
else:
    base_price_usd = 0.0

# បង្ហាញព័ត៌មានភាគរយសន្សំដែលមានស្រាប់ភ្លាមៗនៅពេលវាយកូដត្រូវ
current_discount_pct = 0
is_free = False

if input_code and not df.empty:
    valid_rows = df[df["កូដកាត"] == input_code]
    if not valid_rows.empty:
        idx = valid_rows.index[-1]
        owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
        img_url = df.loc[idx, "រូបភាព"]
        try:
            pts = int(float(df.loc[idx, "ចំនំនួនអ្នកណែនាំ"]))
        except:
            pts = 0
            
        current_discount_pct = pts * 10 if pts < 10 else 100
        if pts >= 10:
            is_free = True
            
        st.markdown(f"### 👤 ព័ត៌មានកូដអតិថិជន")
        col_img, col_info = st.columns([1, 2])
        with col_img:
            if img_url and str(img_url).startswith("http"):
                st.image(img_url, width=120)
            else:
                st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
        with col_info:
            st.write(f"**ឈ្មោះម្ចាស់កូដ:** {owner_name}")
            if is_free:
                st.markdown("**ភាគរយបញ្ចុះតម្លៃបច្ចុប្បន្ន:** <span style='color:green; font-size:20px; font-weight:bold;'>FREE 1 ដង (100%)</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**ភាគរយបញ្ចុះតម្លៃបច្ចុប្បន្ន:** <span style='color:blue; font-size:20px; font-weight:bold;'>{current_discount_pct}%</span> (សន្សំបាន {pts} នាក់)", unsafe_allow_html=True)

st.write("")

# បង្កើតប៊ូតុងជា ២ ជួរឈរធំៗ
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    verify_clicked = st.button("➕ បន្ថែមពិន្ទុថ្មី (+1 នាក់)", type="primary", use_container_width=True)

with btn_col2:
    use_discount_clicked = st.button("🎯 ប្រើប្រាស់ការបញ្ចុះតម្លៃ (គិតលុយ & Reset)", use_container_width=True)

# ករណីចុចប៊ូតុង "➕ បន្ថែមពិន្ទុថ្មី"
if verify_clicked:
    if input_code:
        if not df.empty:
            valid_rows = df[df["កូដកាត"] == input_code]
            
            if not valid_rows.empty:
                idx = valid_rows.index[-1]
                try:
                    current_count = int(float(df.loc[idx, "ចំនំនួនអ្នកណែនាំ"])) + 1
                except:
                    current_count = 1
                    
                owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                img_url = df.loc[idx, "រូបភាព"]
                new_status = "គ្រប់លក្ខខណ្ឌ (Free)" if current_count >= 10 else "សកម្ម"
                
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
                    st.rerun()
                else:
                    st.error("❌ មិនអាចរក្សាទុកទិន្នន័យបានទេ!")
            else:
                st.error(f"❌ មិនមានលេខកូដ {input_code} នេះក្នុងប្រព័ន្ធទេ!")
        else:
            st.error("❌ មិនទាន់មានទិន្នន័យនៅក្នុងតារាងទេ!")
    else:
        st.warning("⚠️ សូមបំពេញលេខកូដកាតជាមុនសិន។")

# ករណីចុចប៊ូតុង "🎯 ប្រើប្រាស់ការបញ្ចុះតម្លៃ" (គណនាលុយជា ២ ជម្រើស រួច Reset)
if use_discount_clicked:
    if input_code:
        if not df.empty:
            valid_rows = df[df["កូដកាត"] == input_code]
            if not valid_rows.empty:
                idx = valid_rows.index[-1]
                owner_name = df.loc[idx, "ឈ្មោះម្ចាស់កូដ"]
                img_url = df.loc[idx, "រូបភាព"]
                
                # គណនាតម្លៃទឹកប្រាក់ជាដុល្លារ
                discount_usd = (base_price_usd * current_discount_pct) / 100
                final_usd = base_price_usd - discount_usd
                
                # គណនាតម្លៃទឹកប្រាក់ជារៀល (ផ្អែកលើលទ្ធផលដុល្លារគុណនឹង 4050)
                final_khr = round(final_usd * EXCHANGE_RATE)
                
                # បង្ហាញលទ្ធផលតម្លៃទឹកប្រាក់ច្បាស់ៗជា ២ ជម្រើស
                st.markdown("---")
                st.markdown("### 🧮 លទ្ធផលនៃការគិតប្រាក់ (អត្រា៖ 1$ = 4,050៛)៖")
                st.write(f"📉 ទទួលបានការបញ្ចុះតម្លៃសរុប៖ **{current_discount_pct}%**")
                
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.markdown(f"<div style='background-color:#f0f2f6; padding:15px; border-radius:10px; text-align:center;'>💵 <b>ទឹកប្រាក់ត្រូវបង់ជា ដុល្លារ</b><br><span style='color:#2e7d32; font-size:28px; font-weight:bold;'>$ {final_usd:,.2f}</span></div>", unsafe_allow_html=True)
                with res_col2:
                    st.markdown(f"<div style='background-color:#f0f2f6; padding:15px; border-radius:10px; text-align:center;'>🇰🇭 <b>ទឹកប្រាក់ត្រូវបង់ជា រៀល</b><br><span style='color:#e65100; font-size:28px; font-weight:bold;'>{final_khr:,.0f} ៛</span></div>", unsafe_allow_html=True)
                st.markdown("---")
                
                # កំណត់ពិន្ទុត្រឡប់ទៅ ០
                params = {
                    "action": "update",
                    "code": input_code,
                    "name": owner_name,
                    "count": 0,
                    "status": "សកម្ម",
                    "image": img_url
                }
                
                with st.spinner("⏳ កំពុងកាត់ពិន្ទុ និងរក្សាទុកទិន្នន័យ..."):
                    response = requests.post(SCRIPT_URL, params=params)
                
                if response.status_code == 200:
                    st.success(f"🎉 បានប្រើប្រាស់ការបញ្ចុះតម្លៃរួចរាល់! កូដរបស់ **{owner_name}** ត្រូវបានកាត់មក ០% វិញហើយ។")
                    st.balloons()
                else:
                    st.error("❌ មិនអាចកែប្រែទិន្នន័យបានទេ!")
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
