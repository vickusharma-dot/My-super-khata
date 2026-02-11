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
st.set_page_config(page_title="Vicky Hub", layout="wide", page_icon="💰")  # Changed to 'wide' for better mobile horizontal buttons

# Enhanced Custom CSS for perfect green buttons + mobile responsive horizontal layout
st.markdown("""
    <style>
    /* Main button styles */
    .stButton > button {
        border: 2px solid #28a745 !important;
        border-radius: 12px !important;
        color: #28a745 !important;
        background-color: white !important;
        font-weight: bold !important;
        height: 2.8em !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    .stButton > button:hover {
        background-color: #28a745 !important;
        color: white !important;
    }
    
    /* Column padding reduction for tighter horizontal fit */
    [data-testid="column"] {
        padding-left: 0.1rem !important;
        padding-right: 0.1rem !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
    }
    
    /* Mobile responsiveness: Shrink buttons & prevent stacking */
    @media screen and (max-width: 768px) {
        .stButton > button {
            padding: 0.4rem 0.4rem !important;
            font-size: 0.85rem !important;
            border-radius: 10px !important;
            height: 2.4em !important;
        }
        [data-testid="column"] {
            padding-left: 0.05rem !important;
            padding-right: 0.05rem !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        .stButton > button {
            padding: 0.3rem 0.3rem !important;
            font-size: 0.75rem !important;
            height: 2.2em !important;
        }
    }
    
    /* General padding fix */
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
    
    st.success("""
    💡 **Tip:** Is app ko phone ki Home Screen par lagane ke liye browser menu (3 dots ⋮) mein 'Install App' ya 'Add to Home Screen' par click karein!
    """)

    st.info("👉 Sidebar se 'Khata App' chuno apna hisab dekhne ke liye.")

    st.markdown("---")
    
    st.markdown("### 🌟 Support Vicky Hub")
    st.write("Bhai, agar meri ye mehnat achi lagi ho, toh apne doston ke sath share zaroor karein! Aapka support hi meri taqat hai.")
    
    share_msg = "Bhai, ye dekh Vicky Hub! Mast digital khata app: https://vicky-khata.streamlit.app"
    st.markdown(f"""
        <a href="whatsapp://send?text={share_msg}" 
           style="background-color: #25D366; color: white; padding: 12px 20px; 
                  text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block; width: 100%; text-align: center;">
           📢 WhatsApp par Share Karein
        </a>
    """, unsafe_allow_html=True)

# --- 6. KHATA APP (Fixed Horizontal Responsive Buttons) ---
elif app_mode == "💰 Khata App":
    st.markdown("<h2 style='text-align: center;'>📊 VICKU KA KHATA</h2>", unsafe_allow_html=True)
    
    if 'choice' not in st.session_state: 
        st.session_state.choice = 'None'

    # FIXED: Horizontal buttons with columns, gap='small', use_container_width=True for mobile auto-adjust
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1], gap="small")
    
    with col1:
        if st.button("➕ Add", use_container_width=True):
            st.session_state.choice = 'add'
    with col2:
        if st.button("📜 Hisab", use_container_width=True):
            st.session_state.choice = 'hisab'
    with col3:
        if st.button("🔍 Search", use_container_width=True):
            st.session_state.choice = 'src'
    with col4:
        if st.button("🤝 Settle", use_container_width=True):
            st.session_state.choice = 'set'
    with col5:
        if st.button("📊 Rep", use_container_width=True):
            st.session_state.choice = 'rep'

    st.divider()

    # Data Fetching
    all_rows = data_sheet.get_all_values()
    if len(all_rows) > 1:
        headers = [h.strip() for h in all_rows[0]]
        df = pd.DataFrame(all_rows[1:], columns=headers)
        if not is_admin:
            df = df[df['User'] == user_logged_in]
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status", "User"])

    val = st.session_state.choice

    if val == 'add':
        with st.form("add_f", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar Diya", "Party", "Shopping", "Other"])
            amt = st.number_input("Amount", min_value=1.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE", use_container_width=True):
                status = "Pending" if cat == "Udhar Diya" else "N/A"
                data_sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, str(amt), note, status, user_logged_in])
                st.success("Entry Saved!")
                st.rerun()

    elif val == 'src':
        # Added basic Search functionality since button exists
        st.subheader("🔍 Search")
        search_term = st.text_input("Search in Notes or Category")
        if search_term:
            filtered = df[df['Note'].str.contains(search_term, case=False, na=False) | 
                          df['Category'].str.contains(search_term, case=False, na=False)]
            if not filtered.empty:
                st.dataframe(filtered, use_container_width=True, hide_index=True)
            else:
                st.info("No results found.")
        else:
            st.info("Enter a search term above.")

    elif val == 'hisab':
        st.subheader("📜 Hisab")
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif val == 'set':
        st.subheader("🤝 Settle Pending")
        pending = df[df['Status'] == 'Pending'].copy()
        if not pending.empty:
            for i, row in pending.iterrows():
                with st.expander(f"₹{row['Amount']} - {row['Note']}"):
                    rec = st.number_input(f"Received?", 0.0, float(row['Amount']), key=f"rec_{i}")
                    if st.button("Settle", key=f"btn_{i}", use_container_width=True):
                        actual_idx = df.index[df.index == i].tolist()[0] + 2  # Sheet indexing
                        total = float(row['Amount'])
                        if rec >= total:
                            data_sheet.update_cell(actual_idx, 5, "Paid ✅")
                        else:
                            data_sheet.update_cell(actual_idx, 5, f"Paid ₹{rec}")
                            data_sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), "Udhar Diya", str(total - rec), f"{row['Note']} (Baki)", "Pending", user_logged_in])
                        st.success("Updated!")
                        st.rerun()
        else: 
            st.info("No pending udhar!")

    elif val == 'rep':
        st.subheader("📊 Report")
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            total_amount = df['Amount'].sum()
            st.metric("TOTAL", f"₹{int(total_amount):,}")
            st.bar_chart(df.groupby('Category')['Amount'].sum())

# --- 7. DIGITAL ATM ---
elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Work in progress...")
