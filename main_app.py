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
    st.error("Sheet Connect Nahi Hui!")

st.set_page_config(page_title="Vicky Khata", layout="centered")

# --- CUSTOM CSS FOR REAL GRID ---
st.markdown("""
    <style>
    /* Buttons ko bada aur touch-friendly banane ke liye */
    div.stButton > button {
        width: 100% !important;
        height: 55px !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        border: 2px solid #4CAF50 !important;
        margin-bottom: -10px;
    }
    /* Mobile screen padding fix */
    .main .block-container { padding: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

if 'choice' not in st.session_state: st.session_state.choice = 'None'

st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📊 VICKY KHATA</h2>", unsafe_allow_html=True)

# --- 2x2 TABLE GRID (No more out of screen) ---
# Row 1
c1, c2 = st.columns(2)
with c1:
    if st.button("➕ Add"): st.session_state.choice = 'add'
with c2:
    if st.button("🤝 Settle"): st.session_state.choice = 'set'

# Row 2
c3, c4 = st.columns(2)
with c3:
    if st.button("📜 Hisab"): st.session_state.choice = 'hisab'
with c4:
    if st.button("📊 Report"): st.session_state.choice = 'rep'

# Niche choti buttons for extra tasks
c5, c6 = st.columns(2)
with c5:
    if st.button("🔍 Search"): st.session_state.choice = 'src'
with c6:
    if st.button("🗑️ Delete"): st.session_state.choice = 'del'

st.divider()

# --- LOGIC ---
val = st.session_state.choice
data = sheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame()

if val == 'add':
    with st.form("a", clear_on_submit=True):
        cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Other"])
        amt = st.number_input("Amount", 0.0)
        note = st.text_input("Note")
        if st.form_submit_button("SAVE"):
            if amt > 0:
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                st.success("Save Ho Gaya!"); st.rerun()

elif val == 'rep':
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        st.markdown(f"## **Total: ₹{df['Amount'].sum()}**")
        summary = df.groupby('Category')['Amount'].sum()
        for k, v in summary.items():
            if v > 0: st.write(f"🔹 {k}: ₹{v}")

elif val == 'hisab':
    st.dataframe(df, use_container_width=True, hide_index=True)

elif val == 'del':
    if len(data) > 1:
        sheet.delete_rows(len(data))
        st.warning("Last Entry Deleted!"); st.session_state.choice = 'None'; st.rerun()
        
