import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# --- GOOGLE SHEETS SETUP ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    SHEET_NAME = "Vicku_khata data" 
    sheet = client.open(SHEET_NAME).sheet1
except Exception as e:
    st.error("❌ Sheet Connect Nahi Hui!")

# --- APP CONFIG ---
st.set_page_config(page_title="Vicky's Hub", layout="centered")

# Sabse pehle Menu select karne ke liye session state
if 'v_menu' not in st.session_state:
    st.session_state.v_menu = 'None'

# Sidebar ko simple rakha hai
app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "💰 Khata App":
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📊 VICKY KHATA</h2>", unsafe_allow_html=True)
    
    # Data fetch kar lo pehle hi
    all_data = sheet.get_all_values()
    headers = [h.strip() for h in all_data[0]] if all_data else []
    df = pd.DataFrame(all_data[1:], columns=headers) if len(all_data) > 1 else pd.DataFrame()

    # --- MOBILE OPTIMIZED GRID ---
    # Column 1 aur Column 2 mein buttons baant di hain
    c1, c2 = st.columns(2)
    
    if c1.button("➕ Add"): st.session_state.v_menu = 'add'
    if c2.button("🤝 Settle"): st.session_state.v_menu = 'settle'
    if c1.button("📜 Hisab"): st.session_state.v_menu = 'hisab'
    if c2.button("🔍 Search"): st.session_state.v_menu = 'search'
    if c1.button("🗑️ Delete"): st.session_state.v_menu = 'delete'
    if c2.button("📊 Report"): st.session_state.v_menu = 'report'

    st.divider()

    # --- FUNCTIONS ---
    v_menu = st.session_state.v_menu

    if v_menu == 'add':
        st.subheader("📝 Nayi Entry")
        with st.form("f1", clear_on_submit=True):
            cat = st.selectbox("Category:", ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"])
            amt = st.number_input("Amount (₹):", min_value=0.0)
            note = st.text_input("Note:")
            if st.form_submit_button("SAVE"):
                if amt > 0:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([now, cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                    st.success("Save Ho Gaya!")
                    st.rerun()

    elif v_menu == 'settle':
        st.subheader("🤝 Udhar Settle")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'] + ")"
                pick = st.selectbox("Kaun?", pending['disp'].tolist())
                pay = st.number_input("Kitne paise mile?", min_value=0.0)
                if st.button("SETTLE NOW"):
                    row_info = pending[pending['disp'] == pick].iloc[0]
                    cell = sheet.find(row_info['Date'])
                    rem = float(row_info['Amount']) - pay
                    if rem <= 0:
                        sheet.update_cell(cell.row, 5, "Paid")
                        sheet.update_cell(cell.row, 3, 0)
                    else:
                        sheet.update_cell(cell.row, 3, rem)
                    st.success("Hisaab Update Hua!")
                    st.rerun()
            else: st.info("Koi Pending Udhar Nahi Hai.")

    elif v_menu == 'hisab':
        st.subheader("📜 History")
        if not df.empty: st.dataframe(df, use_container_width=True)

    elif v_menu == 'search':
        st.subheader("🔍 Search")
        q = st.text_input("Dhundho:")
        if q and not df.empty:
            res = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)

    elif v_menu == 'delete':
        if len(all_data) > 1:
            sheet.delete_rows(len(all_data))
            st.warning("Last Entry Deleted!")
            st.session_state.v_menu = 'None'
            st.rerun()

    elif v_menu == 'report':
        st.subheader("📊 Category Report")
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            summary = df.groupby('Category')['Amount'].sum()
            for k, v in summary.items():
                if v > 0: st.write(f"🔹 **{k}:** ₹{v}")
            st.divider()
            st.markdown(f"### 💰 KUL TOTAL: ₹{df['Amount'].sum()}")

elif app_mode == "🏠 Home":
    st.title("Welcome Vicky!")
    st.write("Bhai sidebar se Khata App chuno.")
    
