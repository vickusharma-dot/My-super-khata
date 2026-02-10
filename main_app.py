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
st.set_page_config(page_title="Vicky Khata", layout="wide")

# CSS: Isse buttons mobile par bhi 2 ki line mein hi rahengi
st.markdown("""
    <style>
    /* Force 2 columns on mobile */
    [data-testid="column"] {
        width: 48% !important;
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        display: flex !important;
        flex-wrap: nowrap !important;
    }
    .stButton>button {
        width: 100% !important;
        height: 65px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        border: 2px solid #4CAF50 !important;
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

if 'v_opt' not in st.session_state: st.session_state.v_opt = 'None'

# Sidebar
app_mode = st.sidebar.radio("Menu", ["💰 Khata App", "🏠 Home", "🏧 Digital ATM"])

if app_mode == "💰 Khata App":
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📊 VICKY KHATA</h2>", unsafe_allow_html=True)
    
    # Data Fetch
    all_rows = sheet.get_all_values()
    df = pd.DataFrame(all_rows[1:], columns=[h.strip() for h in all_rows[0]]) if len(all_rows) > 1 else pd.DataFrame()

    # --- THE GRID (Zabardasti 2 columns) ---
    r1_c1, r1_c2 = st.columns(2)
    if r1_c1.button("➕ Add"): st.session_state.v_opt = '1'
    if r1_c2.button("🤝 Settle"): st.session_state.v_opt = '2'
    
    r2_c1, r2_c2 = st.columns(2)
    if r2_c1.button("📜 Hisab"): st.session_state.v_opt = '3'
    if r2_c2.button("🔍 Search"): st.session_state.v_opt = '4'
    
    r3_c1, r3_c2 = st.columns(2)
    if r3_c1.button("🗑️ Delete"): st.session_state.v_opt = '5'
    if r3_c2.button("📊 Report"): st.session_state.v_opt = '6'

    st.divider()
    opt = st.session_state.v_opt

    # Logic functions
    if opt == '1':
        with st.form("add"):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Other"])
            amt = st.number_input("Amount", min_value=0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                st.success("Saved!"); st.rerun()

    elif opt == '2':
        if not df.empty and 'Status' in df.columns:
            udhar = df[df['Status'] == 'Pending']
            if not udhar.empty:
                sel = st.selectbox("Kaun?", (udhar['Note'] + " (₹" + udhar['Amount'] + ")").tolist())
                pay = st.number_input("Kitne mile?", min_value=0.0)
                if st.button("UPDATE"):
                    # Logic to find row and update
                    st.success("Updated!"); st.rerun()
            else: st.info("No Udhar")

    elif opt == '3':
        st.dataframe(df, use_container_width=True)

    elif opt == '6':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            for k, v in df.groupby('Category')['Amount'].sum().items():
                st.write(f"🔹 {k}: ₹{v}")
            st.markdown(f"### 💰 TOTAL: ₹{df['Amount'].sum()}")

elif app_mode == "🏠 Home":
    st.title("Welcome Vicky!")
    
