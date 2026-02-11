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
    st.error("Sheet Connection Error!")

# --- CONFIG & CSS ---
st.set_page_config(page_title="Vicky's Multi-App Hub", layout="centered")

st.markdown("""
    <style>
    div.stButton > button {
        width: 100% !important;
        height: 55px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        border: 2px solid #4CAF50 !important;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR MENU (Home, Khata, ATM) ---
st.sidebar.title("🚀 Vicky Hub")
app_mode = st.sidebar.radio("App Chuno:", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

# --- 🏠 HOME SCREEN ---
if app_mode == "🏠 Home":
    st.title("Welcome Vicky! 😎")
    st.write("Bhai, ye tera digital adda hai. Sidebar se koi bhi app select kar.")
    st.info("Khata App: Paise ka hisab rakhne ke liye\n\nATM: Digital cash check karne ke liye")

# --- 💰 KHATA APP ---
elif app_mode == "💰 Khata App":
    st.markdown("<h2 style='text-align: center;'>📊 VICKY KHATA</h2>", unsafe_allow_html=True)
    
    if 'v_choice' not in st.session_state: st.session_state.v_choice = 'None'

    # Buttons Grid (Forced side-by-side)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add"): st.session_state.v_choice = 'add'
        if st.button("📜 Hisab"): st.session_state.v_choice = 'hisab'
    with c2:
        if st.button("🤝 Settle"): st.session_state.v_choice = 'set'
        if st.button("📊 Report"): st.session_state.v_choice = 'rep'
    
    # Extra Options below
    c3, c4 = st.columns(2)
    if c3.button("🔍 Search"): st.session_state.v_choice = 'src'
    if c4.button("🗑️ Delete"): st.session_state.v_choice = 'del'

    st.divider()
    
    # Logic
    val = st.session_state.v_choice
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame()

    if val == 'add':
        with st.form("add_form"):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Safar", "Other"])
            amt = st.number_input("Amount (₹)", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                st.success("Entry Saved!"); st.rerun()

    elif val == 'rep':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.markdown(f"### 💰 Total: ₹{df['Amount'].sum()}")
            for k, v in df.groupby('Category')['Amount'].sum().items():
                if v > 0: st.write(f"🔹 **{k}:** ₹{v}")

    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif val == 'del':
        if len(data) > 1:
            sheet.delete_rows(len(data))
            st.warning("Last Entry Deleted!"); st.rerun()

# --- 🏧 ATM APP ---
elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Bhai, ATM feature abhi testing mein hai. Jald hi chalu hoga!")
    st.image("https://cdn-icons-png.flaticon.com/512/2782/2782058.png", width=100)
