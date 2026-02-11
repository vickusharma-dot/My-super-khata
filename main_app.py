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
except Exception as e:
    st.error(f"Sheet Error: {e}")

st.set_page_config(page_title="Vicky Multi-Khata", layout="centered")

# --- CSS (TERA LATEST STYLE) ---
st.markdown("""
    <style>
    .stButton > button {
        width: auto !important; min-width: 90px !important; height: 50px !important;
        margin: 4px 6px !important; border-radius: 10px !important;
        border: 2px solid #4CAF50 !important; font-weight: bold !important;
    }
    section.main > div.block-container { overflow-x: hidden !important; padding-bottom: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("👤 Kaun ho bhai?")
    u_name = st.text_input("Apna Naam Likho (Username):").strip().lower()
    if st.button("Pura Khata Khola Jaye 🚀"):
        if u_name:
            st.session_state.user = u_name
            st.rerun()
        else:
            st.warning("Naam toh batao!")
    st.stop()

# --- APP START ---
user_logged_in = st.session_state.user
is_admin = False

# EMERGENCY HOLE: Agar tumhara naam 'vickyadmin' hai toh sab dikhega
if user_logged_in == "vicky786": # Ye teri secret key hai
    is_admin = True

st.sidebar.write(f"Logged in as: **{user_logged_in.upper()}**")
if st.sidebar.button("Logout 🚪"):
    st.session_state.user = None
    st.rerun()

app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title(f"Welcome {user_logged_in.upper()}! 😎")
    st.info("Bhai, niche button se apna hisab manage karo.")

elif app_mode == "💰 Khata App":
    st.markdown(f"<h3 style='text-align: center;'>📊 {user_logged_in.upper()} KA KHATA</h3>", unsafe_allow_html=True)
    
    if 'choice' not in st.session_state: st.session_state.choice = 'None'

    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("➕ Add"): st.session_state.choice = 'add'
        if st.button("📜 Hisab"): st.session_state.choice = 'hisab'
        if st.button("🔍 Search"): st.session_state.choice = 'src'
        if st.button("🤝 Settle"): st.session_state.choice = 'set'
        if st.button("📊 Report"): st.session_state.choice = 'rep'
        if st.button("🗑️ Delete"): st.session_state.choice = 'del'

    st.divider()

    # Data Fetching
    data_values = sheet.get_all_values()
    if len(data_values) > 1:
        cols = [c.strip() for c in data_values[0]]
        full_df = pd.DataFrame(data_values[1:], columns=cols)
        
        # PRIVACY FILTER: Admin ko sab dikhega, baki ko sirf apna
        if is_admin:
            df = full_df
            st.sidebar.warning("⚡ ADMIN MODE ON")
        else:
            if 'User' in full_df.columns:
                df = full_df[full_df['User'] == user_logged_in]
            else:
                df = pd.DataFrame(columns=cols)
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status", "User"])

    val = st.session_state.choice

    if val == 'add':
        with st.form("a", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Safar", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                # Naya column 'User' save ho raha hai
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, str(amt), note, "Pending" if cat=="Udhar" else "N/A", user_logged_in])
                st.success("Saved!"); st.rerun()

    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif val == 'rep':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.metric("TOTAL", f"₹{df['Amount'].sum():,.0f}")
            st.bar_chart(df.groupby('Category')['Amount'].sum())
        else: st.info("Khali hai!")

    elif val == 'del':
        if not df.empty:
            st.warning("Aakhri entry delete karein?")
            if st.button("HAAN"):
                # Yahan logic ye hai ki sheet se wahi row delete hogi jo user ki aakhri hai
                # Par simplicity ke liye hum user ko uske data mein dikha rahe hain
                st.info("Admin se contact karein delete ke liye safety ke liye.")
                
