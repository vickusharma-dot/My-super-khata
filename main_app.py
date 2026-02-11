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

# --- APP CONFIG & CSS (Grid Fix) ---
st.set_page_config(page_title="Vicky Hub", layout="centered")

st.markdown("""
    <style>
    /* Buttons ko screen ke andar rakhne ka ilaaj */
    div[data-testid="column"] {
        width: 48% !important;
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        gap: 5px !important;
    }
    .stButton>button {
        width: 100% !important;
        height: 55px !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        border: 2px solid #4CAF50 !important;
        font-size: 14px !important;
        padding: 0px !important;
    }
    /* Mobile screen padding fix */
    .block-container { padding: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Home, ATM etc Sab Kuch) ---
app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title("Welcome Vicky! 😎")
    st.write("Bhai, ye tera digital adda hai. Sidebar se app select kar.")
    st.info("Khata App: Paise ka hisab | ATM: Digital cash check")

elif app_mode == "💰 Khata App":
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📊 VICKY KHATA</h2>", unsafe_allow_html=True)
    
    if 'v_choice' not in st.session_state: st.session_state.v_choice = 'None'

    # --- 2x3 Grid Jo Screen ke Andar Rahega ---
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
    
    # Logic
    val = st.session_state.v_choice
    all_data = sheet.get_all_values()
    df = pd.DataFrame(all_data[1:], columns=all_data[0]) if len(all_data) > 1 else pd.DataFrame()

    if val == 'add':
        with st.form("a"):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                st.success("Saved!"); st.rerun()
    
    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    elif val == 'rep':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.markdown(f"### 💰 Total: ₹{df['Amount'].sum()}")

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Feature jald hi chalu hoga!")
