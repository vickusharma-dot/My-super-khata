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
    sheet = client.open("Vicku_khata data").sheet1
except:
    st.error("Sheet Error!")

st.set_page_config(page_title="Vicky Hub", layout="centered")

# --- CUSTOM CSS FOR BUTTONS + HORIZONTAL FIX ---
st.markdown("""
    <style>
    .stButton > button {
        width: auto !important;
        min-width: 90px !important;
        height: 50px !important;
        margin: 4px 6px !important;
        padding: 0 12px !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        border: 2px solid #4CAF50 !important;
        font-weight: bold !important;
        white-space: nowrap !important;
    }
    /* Horizontal scroll rokne ke liye safety */
    section.main > div.block-container {
        overflow-x: hidden !important;
        padding-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

if 'choice' not in st.session_state:
    st.session_state.choice = 'None'

# --- SIDEBAR MENU ---
app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title("Welcome Vicky! 😎")
    st.info("Bhai, Sidebar se app chuno.")

elif app_mode == "💰 Khata App":
    st.markdown("<h3 style='text-align: center;'>📊 VICKY KHATA</h3>", unsafe_allow_html=True)
    
    # Horizontal buttons – mobile pe bhi side-by-side + no horizontal scroll
    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("➕ Add", key="btn_add"):
            st.session_state.choice = 'add'
        
        if st.button("📜 Hisab", key="btn_hisab"):
            st.session_state.choice = 'hisab'
        
        if st.button("🔍 Search", key="btn_src"):
            st.session_state.choice = 'src'
        
        if st.button("🤝 Settle", key="btn_set"):
            st.session_state.choice = 'set'
        
        if st.button("📊 Report", key="btn_rep"):
            st.session_state.choice = 'rep'
        
        if st.button("🗑️ Delete", key="btn_del"):
            st.session_state.choice = 'del'

    st.divider()
    
    # Data & Logic
    val = st.session_state.choice
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame()

    if val == 'add':
        with st.form("a", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Safar", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                st.success("Saved!")
                st.rerun()

    elif val == 'rep':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            summary = df.groupby('Category')['Amount'].sum()
            for k, v in summary.items():
                if v > 0:
                    st.write(f"🔹 **{k}:** ₹{v:,.0f}")
            st.markdown(f"## **Total: ₹{df['Amount'].sum():,.0f}**")

    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif val == 'set':
        st.subheader("🤝 Udhar Settle")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'].astype(str) + ")"
                pick = st.selectbox("Kiska udhar?", pending['disp'].tolist())
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
                    st.success("Update Ho Gaya!")
                    st.rerun()
            else:
                st.info("Koi pending nahi hai.")

    elif val == 'src':
        st.info("Search feature abhi under development hai bhai!")

    elif val == 'del':
        st.info("Delete feature abhi under development hai bhai!")

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Bhai, feature jald aayega!")
