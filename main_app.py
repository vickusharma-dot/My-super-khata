import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# --- SETUP ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Vicku_khata data").sheet1
except:
    st.error("Sheet error!")

st.set_page_config(page_title="Vicky Khata", layout="centered")

# --- FORCED CSS GRID (ISSE PAKKA 2 COLUMNS DIKHENGE) ---
st.markdown("""
    <style>
    /* Buttons ko side-by-side lane ke liye */
    div[data-testid="column"] {
        width: 48% !important;
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }
    .stButton>button {
        width: 100% !important;
        height: 60px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        border: 2px solid #4CAF50 !important;
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

if 'v_choice' not in st.session_state: st.session_state.v_choice = 'None'

st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📊 VICKY KHATA</h2>", unsafe_allow_html=True)

# --- 2x3 GRID LAYOUT ---
c1, c2 = st.columns(2)
if c1.button("➕ Add"): st.session_state.v_choice = 'add'
if c2.button("🤝 Settle"): st.session_state.v_choice = 'set'

c3, c4 = st.columns(2)
if c3.button("📜 Hisab"): st.session_state.v_choice = 'hisab'
if c4.button("📊 Report"): st.session_state.v_choice = 'rep'

c5, c6 = st.columns(2)
if c5.button("🔍 Search"): st.session_state.v_choice = 'src'
if c6.button("🗑️ Delete"): st.session_state.v_choice = 'del'

st.divider()

# --- LOGIC SECTIONS ---
choice = st.session_state.v_choice
data = sheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame()

if choice == 'add':
    with st.form("a", clear_on_submit=True):
        cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Other"])
        amt = st.number_input("Amount", 0.0)
        note = st.text_input("Note")
        if st.form_submit_button("SAVE"):
            sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
            st.success("Save Ho Gaya!"); st.rerun()

elif choice == 'rep':
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        st.markdown(f"## **Total: ₹{df['Amount'].sum()}**")
        summary = df.groupby('Category')['Amount'].sum()
        for k, v in summary.items():
            if v > 0: st.write(f"🔹 **{k}:** ₹{v}")

elif choice == 'hisab':
    st.dataframe(df, use_container_width=True, hide_index=True)

elif choice == 'del':
    if len(data) > 1:
        sheet.delete_rows(len(data))
        st.warning("Last Entry Deleted!"); st.session_state.v_choice = 'None'; st.rerun()
