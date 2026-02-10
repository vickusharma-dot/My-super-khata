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
except Exception as e:
    st.error("Sheet link fail!")

st.set_page_config(page_title="Vicky Khata", layout="centered")

# --- KADAK CSS (FORCED GRID) ---
st.markdown("""
    <style>
    /* Sabhi buttons ko dabba mein fit karne ke liye */
    .main-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        width: 100%;
    }
    div.stButton > button {
        width: 100% !important;
        height: 60px !important;
        border-radius: 10px !important;
        border: 2px solid #4CAF50 !important;
        background-color: white !important;
        color: black !important;
        font-weight: bold !important;
    }
    /* Mobile fix for sidebar */
    [data-testid="stSidebarNav"] { display: block !important; }
    </style>
    """, unsafe_allow_html=True)

if 'choice' not in st.session_state: st.session_state.choice = 'None'

# Sidebar
menu = st.sidebar.radio("Main Menu", ["💰 Khata App", "🏠 Home"])

if menu == "💰 Khata App":
    st.markdown("<h2 style='text-align: center;'>📊 VICKY KHATA</h2>", unsafe_allow_html=True)
    
    # Grid Buttons - Ek line mein 2 buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add"): st.session_state.choice = 'add'
        if st.button("📜 Hisab"): st.session_state.choice = 'hisab'
        if st.button("🗑️ Delete"): st.session_state.choice = 'del'
    with col2:
        if st.button("🤝 Settle"): st.session_state.choice = 'set'
        if st.button("🔍 Search"): st.session_state.choice = 'src'
        if st.button("📊 Report"): st.session_state.choice = 'rep'

    st.divider()
    val = st.session_state.choice

    # Fetch Data
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame()

    if val == 'add':
        with st.form("a"):
            c = st.selectbox("Kya?", ["Khana", "Petrol", "Udhar", "Other"])
            a = st.number_input("Amount", 0.0)
            n = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d"), c, a, n, "Pending" if c=="Udhar" else "N/A"])
                st.success("Done!"); st.rerun()

    elif val == 'rep':
        st.subheader("💰 Report")
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            # Category wise Total
            cats = df.groupby('Category')['Amount'].sum()
            for k, v in cats.items():
                st.write(f"🔹 **{k}:** ₹{v}")
            st.markdown(f"## **Total: ₹{df['Amount'].sum()}**")
            
    elif val == 'hisab':
        st.dataframe(df, use_container_width=True)

    elif val == 'set':
        st.write("Udhar settle option yahan aayega...")

elif menu == "🏠 Home":
    st.title("Welcome Bhai!")
    
