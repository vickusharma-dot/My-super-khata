import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# --- 1. DATABASE CONNECTION ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    main_sheet = client.open("Vicku_khata data")
    data_sheet = main_sheet.sheet1
    try:
        user_sheet = main_sheet.worksheet("Users")
    except:
        user_sheet = main_sheet.add_worksheet(title="Users", rows="100", cols="2")
        user_sheet.append_row(["Username", "PIN"])
except Exception as e:
    st.error(f"Sheet Connectivity Error: {e}")

# --- 2. CONFIG & CUSTOM CSS ---
st.set_page_config(page_title="Vicky Hub", layout="wide", page_icon="💰")

st.markdown("""
    <style>
    /* BIG VIEW BUTTON - Full width & prominent */
    .view-btn > button {
        border: 3px solid #28a745 !important;
        border-radius: 15px !important;
        color: #28a745 !important;
        background-color: white !important;
        font-weight: bold !important;
        font-size: 1.3em !important;
        height: 3.5em !important;
        width: 100% !important;
        margin: 1rem 0 !important;
    }
    .view-btn > button:hover {
        background-color: #28a745 !important;
        color: white !important;
        transform: scale(1.02) !important;
    }
    
    /* Mobile perfect */
    @media screen and (max-width: 768px) {
        .view-btn > button {
            font-size: 1.1em !important;
            height: 3.2em !important;
            border-radius: 12px !important;
        }
    }
    
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN LOGIC ---
if 'user' not in st.session_state: 
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Vicky Hub Login")
    u_input = st.text_input("Username")
    p_input = st.text_input("4-Digit PIN", type="password")
    if st.button("Login / Register 🚀", use_container_width=True):
        u_clean = u_input.strip().lower()
        if u_clean and len(p_input) == 4 and p_input.isdigit():
            user_data = user_sheet.get_all_records()
            existing_user = next((item for item in user_data if item["Username"] == u_clean), None)
            if existing_user:
                if str(existing_user["PIN"]) == p_input:
                    st.session_state.user = u_clean
                    st.rerun()
                else: 
                    st.error("Galat PIN! ❌")
            else:
                user_sheet.append_row([u_clean, p_input])
                st.session_state.user = u_clean
                st.rerun()
    st.stop()

# --- 4. NAVIGATION ---
user_logged_in = st.session_state.user
is_admin = (user_logged_in == "vicky786")
app_mode = st.sidebar.radio("Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if st.sidebar.button("Logout 🚪", use_container_width=True):
    st.session_state.user = None
    st.session_state.choice = 'None'
    st.rerun()

# --- 5. HOME PAGE ---
if app_mode == "🏠 Home":
    st.title(f"Welcome, {user_logged_in.upper()}! ✨")
    st.success("💡 Phone ki Home Screen par app install kar lo!")
    st.info("👉 Sidebar se 'Khata App' chuno!")

# --- 6. KHATA APP (SINGLE BIG VIEW BUTTON) ---
elif app_mode == "💰 Khata App":
    st.markdown("<h1 style='text-align: center; color: #28a745;'>📊 VICKU KA KHATA</h1>", unsafe_allow_html=True)
    
    if 'choice' not in st.session_state: 
        st.session_state.choice = 'None'

    # BIG CENTERED VIEW BUTTON - Exactly like your screenshot
    st.markdown("---")
    st.markdown("<div style='text-align: center; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    if st.button("🔍 **VIEW HISAB**", key="big_view_btn", help="Apna pura hisab dekho!"):
        st.session_state.choice = 'view'
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

    # Data Fetching
    all_rows = data_sheet.get_all_values()
    if len(all_rows) > 1:
        headers = [h.strip() for h in all_rows[0]]
        df = pd.DataFrame(all_rows[1:], columns=headers)
        if not is_admin:
            df = df[df['User'] == user_logged_in]
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status", "User"])

    if st.session_state.choice == 'view':
        st.markdown("<h2 style='text-align: center; color: #28a745;'>👀 **APNA PURA HISAB**</h2>", unsafe_allow_html=True)
        
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            total = df['Amount'].sum()
            pending_df = df[df['Status'] == 'Pending']
            pending_amt = pending_df['Amount'].sum() if not pending_df.empty else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 TOTAL", f"₹{int(total):,}")
            col2.metric("⏳ UDHAR", f"₹{int(pending_amt):,}")
            col3.metric("✅ PAID", f"₹{int(total-pending_amt):,}")
            
            st.divider()
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.subheader("📈 Category Chart")
            st.bar_chart(df.groupby('Category')['Amount'].sum())
            
            if not pending_df.empty:
                st.subheader("⚠️ PENDING ITEMS")
                st.dataframe(pending_df, use_container_width=True, hide_index=True)
            else:
                st.success("🎉 Koi udhar nahi baki!")
        else:
            st.info("📝 Pehli entry add karne ke liye admin se bolo!")

# --- 7. DIGITAL ATM ---
elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Work in progress...")
