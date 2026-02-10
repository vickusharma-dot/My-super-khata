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
st.set_page_config(page_title="Vicky's Hub", layout="wide")

# Custom CSS for Full Width Buttons
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 60px;
        background-color: #F0F2F6;
        font-size: 18px;
        font-weight: bold;
        border: 2px solid #4CAF50;
        margin-bottom: 10px;
    }
    div.stButton > button:hover {
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation
app_mode = st.sidebar.radio("Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title("🚀 Vicky's Digital Hub")
    st.success("Bhai, sidebar se 'Khata App' chuno kaam shuru karne ke liye!")

elif app_mode == "💰 Khata App":
    st.markdown("<h2 style='text-align: center;'>📊 VICKY KHATA SYSTEM</h2>", unsafe_allow_html=True)
    
    # Fresh Data Fetch
    all_data = sheet.get_all_values()
    headers = [h.strip() for h in all_data[0]] if all_data else []
    df = pd.DataFrame(all_data[1:], columns=headers) if len(all_data) > 1 else pd.DataFrame()

    # --- GRID BUTTONS (2 Columns, Full Width) ---
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ 1. Naya Kharcha"): st.session_state.opt = '1'
        if st.button("📜 3. Pura Hisab"): st.session_state.opt = '3'
        if st.button("🗑️ 5. Delete Last"): st.session_state.opt = '5'
        
    with col2:
        if st.button("🤝 2. Udhar Settle"): st.session_state.opt = '2'
        if st.button("🔍 4. Search"): st.session_state.opt = '4'
        if st.button("📊 6. Report & Total"): st.session_state.opt = '6'

    st.divider()

    # Current Selection Logic
    opt = st.session_state.get('opt', None)

    # 1. ADD
    if opt == '1':
        st.subheader("📝 Naya Kharcha Entry")
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            cat = c1.selectbox("Category:", ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"])
            amt = c2.number_input("Amount (₹):", min_value=0.0)
            note = st.text_input("Note (Kiske liye?):")
            if st.form_submit_button("💾 Save To Sheet"):
                if amt > 0:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([now, cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                    st.success("Entry Saved!")
                    st.rerun()

    # 2. SETTLE (PARTIAL)
    elif opt == '2':
        st.subheader("🤝 Udhar Settle Karein")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'] + ")"
                pick = st.selectbox("Kiska hisab karna hai?", pending['disp'].tolist())
                received = st.number_input("Kitne paise mile?", min_value=0.0)
                if st.button("Confirm Settle"):
                    row_info = pending[pending['disp'] == pick].iloc[0]
                    cell = sheet.find(row_info['Date'])
                    rem = float(row_info['Amount']) - received
                    if rem <= 0:
                        sheet.update_cell(cell.row, 5, "Paid")
                        sheet.update_cell(cell.row, 3, 0)
                        st.success("Hisaab Pura Clear!")
                    else:
                        sheet.update_cell(cell.row, 3, rem)
                        st.warning(f"₹{rem} abhi bhi baaki hain.")
                    st.rerun()
            else: st.info("Koi udhar pending nahi hai.")

    # 3. HISTORY
    elif opt == '3':
        st.subheader("📜 Sabhi Transactions")
        if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)

    # 4. SEARCH
    elif opt == '4':
        st.subheader("🔍 Search")
        q = st.text_input("Kya dhundna hai?")
        if q and not df.empty:
            res = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)

    # 5. DELETE
    elif opt == '5':
        if len(all_data) > 1:
            sheet.delete_rows(len(all_data))
            st.error("Aakhri line delete ho gayi!")
            st.session_state.opt = None
            st.rerun()

    # 6. REPORT (SIMPLE TEXT)
    elif opt == '6':
        st.subheader("📊 Category-wise Summary")
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            summary = df.groupby('Category')['Amount'].sum()
            
            for category, total in summary.items():
                if total > 0:
                    st.markdown(f"✅ **{category}:** ₹{total}")
            
            st.divider()
            st.markdown(f"<h2 style='color: #4CAF50;'>💰 Kul Total Kharcha: ₹{df['Amount'].sum()}</h2>", unsafe_allow_html=True)

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.info("Coming Soon...")
