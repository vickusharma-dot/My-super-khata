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

# --- APP CONFIG (FULL WIDTH) ---
st.set_page_config(page_title="Vicky's Hub", layout="wide")

# CSS for full-width grid buttons
st.markdown("""
    <style>
    .stButton>button {
        width: 100% !important;
        height: 70px !important;
        border-radius: 15px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        background-color: #F0F2F6 !important;
        border: 2px solid #4CAF50 !important;
    }
    .stButton>button:active, .stButton>button:focus {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
app_mode = st.sidebar.radio("Main Menu", ["💰 Khata App", "🏠 Home", "🏧 Digital ATM"])

if app_mode == "💰 Khata App":
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📊 VICKY KHATA SYSTEM</h2>", unsafe_allow_html=True)
    
    # Fresh Data Fetch
    all_data = sheet.get_all_values()
    headers = [h.strip() for h in all_data[0]] if all_data else []
    df = pd.DataFrame(all_data[1:], columns=headers) if len(all_data) > 1 else pd.DataFrame()

    # --- 2x3 GRID BUTTONS ---
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ 1. Add"): st.session_state.v_opt = '1'
        if st.button("📜 3. Hisab"): st.session_state.v_opt = '3'
        if st.button("🗑️ 5. Delete"): st.session_state.v_opt = '5'
        
    with col2:
        if st.button("🤝 2. Settle"): st.session_state.v_opt = '2'
        if st.button("🔍 4. Search"): st.session_state.v_opt = '4'
        if st.button("📊 6. Report"): st.session_state.v_opt = '6'

    st.divider()

    # Logic
    v_opt = st.session_state.get('v_opt', None)

    if v_opt == '1':
        st.subheader("📝 Nayi Entry")
        with st.form("add_f"):
            c1, c2 = st.columns(2)
            cat = c1.selectbox("Kaunsa:", ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"])
            amt = c2.number_input("Amount (₹):", min_value=0.0)
            note = st.text_input("Note:")
            if st.form_submit_button("SAVE"):
                if amt > 0:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([now, cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                    st.success("Saved!")
                    st.rerun()

    elif v_opt == '2':
        st.subheader("🤝 Udhar Settle")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'] + ")"
                pick = st.selectbox("Kaun?", pending['disp'].tolist())
                pay = st.number_input("Amount mila?", min_value=0.0)
                if st.button("SETTLE"):
                    row_info = pending[pending['disp'] == pick].iloc[0]
                    cell = sheet.find(row_info['Date'])
                    rem = float(row_info['Amount']) - pay
                    if rem <= 0:
                        sheet.update_cell(cell.row, 5, "Paid")
                        sheet.update_cell(cell.row, 3, 0)
                    else:
                        sheet.update_cell(cell.row, 3, rem)
                    st.success("Updated!")
                    st.rerun()
            else: st.info("No pending udhar.")

    elif v_opt == '3':
        st.subheader("📜 History")
        if not df.empty: st.dataframe(df, use_container_width=True)

    elif v_opt == '4':
        st.subheader("🔍 Search")
        q = st.text_input("Find:")
        if q and not df.empty:
            res = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)

    elif v_opt == '5':
        if len(all_data) > 1:
            sheet.delete_rows(len(all_data))
            st.warning("Last Entry Deleted!")
            st.rerun()

    elif v_opt == '6':
        st.subheader("📊 Category Report")
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            summary = df.groupby('Category')['Amount'].sum()
            for k, v in summary.items():
                if v > 0: st.write(f"🔹 **{k}:** ₹{v}")
            st.divider()
            st.markdown(f"### 💰 KUL TOTAL: ₹{df['Amount'].sum()}")

elif app_mode == "🏠 Home":
    st.title("🚀 Welcome Vicky!")
    st.write("Sidebar se Khata App chuno.")

else:
    st.title("🏧 ATM")
    st.info("Side mein hai...")
