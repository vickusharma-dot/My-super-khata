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

# --- 2. CONFIG & UI ---
st.set_page_config(page_title="Vicky Hub", layout="centered", page_icon="💰")

st.markdown("""
    <style>
    .stButton > button { width: auto !important; min-width: 90px !important; height: 45px !important; border-radius: 10px !important; font-weight: bold !important; }
    div[data-testid="stExpander"] { border: 1px solid #4CAF50 !important; border-radius: 10px !important; margin-bottom: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN LOGIC ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Vicky Hub Login")
    u_input = st.text_input("Username").strip().lower()
    p_input = st.text_input("4-Digit PIN", type="password")
    if st.button("Login / Register 🚀"):
        if u_input and len(p_input) == 4 and p_input.isdigit():
            user_data = user_sheet.get_all_records()
            existing_user = next((item for item in user_data if item["Username"] == u_input), None)
            if existing_user:
                if str(existing_user["PIN"]) == p_input:
                    st.session_state.user = u_input
                    st.rerun()
                else: st.error("Galat PIN! ❌")
            else:
                user_sheet.append_row([u_input, p_input])
                st.session_state.user = u_input
                st.rerun()
        else: st.warning("Naam aur 4-digit PIN dalo!")
    st.stop()

# --- 4. NAVIGATION ---
user_logged_in = st.session_state.user
is_admin = (user_logged_in == "vicky786")

app_mode = st.sidebar.radio("Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if st.sidebar.button("Logout 🚪"):
    st.session_state.user = None
    st.rerun()

# --- 5. HOME PAGE ---
if app_mode == "🏠 Home":
    # Simple & Clean Welcome
    st.title(f"Welcome, {user_logged_in.upper()}! ✨")
    
    st.success("""
    💡 **Tip:** Is app ko phone ki Home Screen par lagane ke liye browser menu (3 dots ⋮) mein 'Install App' ya 'Add to Home Screen' par click karein!
    """)

    st.info("👉 Sidebar se 'Khata App' chuno apna hisab dekhne ke liye.")
    
    st.markdown("---")
    
    st.markdown("### 🌟 Support Vicky Hub")
    st.write("Bhai, agar meri ye mehnat achi lagi ho, toh apne doston ke sath share zaroor karein aur unhe bhi iske baare mein batayein! Aapka support hi meri taqat hai.")
    
    share_msg = "Bhai, ye dekh Vicky Hub! Mast digital khata app hai, tu bhi use kar: https://vicky-khata.streamlit.app"
    st.markdown(f"""
        <a href="whatsapp://send?text={share_msg}" data-action="share/whatsapp/share" 
           style="background-color: #25D366; color: white; padding: 12px 20px; 
                  text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block;">
           📢 WhatsApp par Share Karein
        </a>
    """, unsafe_allow_html=True)

# --- 6. KHATA APP ---
elif app_mode == "💰 Khata App":
    st.markdown(f"<h3 style='text-align: center;'>📊 {user_logged_in.upper()} KA KHATA</h3>", unsafe_allow_html=True)
    if 'choice' not in st.session_state: st.session_state.choice = 'None'

    with st.container():
        cols = st.columns(5)
        if cols[0].button("➕ Add"): st.session_state.choice = 'add'
        if cols[1].button("📜 Hisab"): st.session_state.choice = 'hisab'
        if cols[2].button("🔍 Search"): st.session_state.choice = 'src'
        if cols[3].button("🤝 Settle"): st.session_state.choice = 'set'
        if cols[4].button("📊 Report"): st.session_state.choice = 'rep'

    st.divider()

    all_rows = data_sheet.get_all_values()
    if len(all_rows) > 1:
        headers = [h.strip() for h in all_rows[0]]
        full_df = pd.DataFrame(all_rows[1:], columns=headers)
        df = full_df if is_admin else full_df[full_df['User'] == user_logged_in]
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status", "User"])

    val = st.session_state.choice

    if val == 'add':
        with st.form("add_form", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar Diya", "Party", "Shopping", "Other"])
            amt = st.number_input("Amount", min_value=1.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                status = "Pending" if cat == "Udhar Diya" else "N/A"
                data_sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, str(amt), note, status, user_logged_in])
                st.success("Save ho gaya!"); st.rerun()

    elif val == 'set':
        # Partial Payment Logic: 500 -> 200 = 300 Balance
        pending_udhar = df[df['Status'] == 'Pending'].copy()
        if not pending_udhar.empty:
            st.write("### 🤝 Paisa Wapas Aaya?")
            for i, row in pending_udhar.iterrows():
                with st.expander(f"₹{row['Amount']} - {row['Note']}"):
                    received = st.number_input(f"Kitna wapas mila?", min_value=0.0, max_value=float(row['Amount']), key=f"inp_{i}")
                    if st.button("Update Karein", key=f"upd_{i}"):
                        if received > 0:
                            actual_idx = full_df.index[full_df.index == i].tolist()[0] + 2
                            total_amt = float(row['Amount'])
                            if received == total_amt:
                                data_sheet.update_cell(actual_idx, 5, "Paid ✅")
                                st.success("Pura Udhar Settle!")
                            else:
                                remaining = total_amt - received
                                data_sheet.update_cell(actual_idx, 5, f"Paid ₹{received}")
                                data_sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), "Udhar Diya", str(remaining), f"{row['Note']} (Baki)", "Pending", user_logged_in])
                                st.warning(f"₹{received} mil gaye. ₹{remaining} baki hain.")
                            st.rerun()
                        else: st.error("Amount dalo!")
        else: st.info("Sab Paisa Vasool Hai! 😎")

    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif val == 'rep':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.metric("KUL KHARCHA", f"₹{df['Amount'].sum():,.0f}")
            st.bar_chart(df.groupby('Category')['Amount'].sum())

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Vicky bhai, ispe kaam chal raha hai. Jald update milega!")
                                                     
