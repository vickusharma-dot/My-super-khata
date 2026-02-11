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
    sheet = main_sheet.sheet1
    try:
        user_sheet = main_sheet.worksheet("Users")
    except:
        user_sheet = main_sheet.add_worksheet(title="Users", rows="100", cols="2")
        user_sheet.append_row(["Username", "PIN"])
except Exception as e:
    st.error("Sheet Connection Error!")

st.set_page_config(page_title="Vicky Hub", layout="centered", page_icon="💰")

# --- 2. TERA WALA CSS (AS IT IS) ---
st.markdown("""
    <style>
    .stButton > button {
        width: auto !important;
        min-width: 90px !important;
        height: 50px !important;
        margin: 4px 6px !important;
        padding: 0 12px !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        border: 2px solid #4CAF50 !important;
        font-weight: bold !important;
        white-space: nowrap !important;
    }
    section.main > div.block-container {
        overflow-x: hidden !important;
        padding-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN SYSTEM (Added Security) ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Vicky Hub Login")
    u_input = st.text_input("Username").strip().lower()
    p_input = st.text_input("4-Digit PIN", type="password")
    if st.button("Login / Register 🚀"):
        if u_input and len(p_input) == 4:
            user_data = user_sheet.get_all_records()
            existing = next((i for i in user_data if i["Username"] == u_input), None)
            if existing:
                if str(existing["PIN"]) == p_input:
                    st.session_state.user = u_input
                    st.rerun()
                else: st.error("Wrong PIN! ❌")
            else:
                user_sheet.append_row([u_input, p_input])
                st.session_state.user = u_input
                st.rerun()
    st.stop()

# --- 4. NAVIGATION ---
user_logged_in = st.session_state.user
if 'choice' not in st.session_state: st.session_state.choice = 'None'
app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if st.sidebar.button("Logout 🚪"):
    st.session_state.user = None
    st.rerun()

# --- 5. HOME PAGE (Restored All Your Lines) ---
if app_mode == "🏠 Home":
    st.title(f"Welcome {user_logged_in.upper()}! 😎")
    
    st.success("💡 **Tip:** Is app ko phone ki Home Screen par lagane ke liye browser menu (3 dots ⋮) mein 'Install App' ya 'Add to Home Screen' par click karein!")
    
    st.markdown("### 📢 Naya Kya Hai?")
    st.markdown("* 📲 **Smart Install:** Browser ab install ka option dega.\n* 🔐 **My Privacy:** Aapka data sirf aapke PIN se khulega.")
    
    st.info("👉 Sidebar se 'Khata App' chuno apna hisab dekhne ke liye.")
    
    st.markdown("---")
    st.markdown("### 🌟 Support Vicky Hub")
    st.write("Bhai, agar meri ye mehnat achi lagi ho, toh apne doston ke sath share zaroor karein!")
    
    share_msg = "Bhai, ye dekh Vicky Hub! Mast digital khata app: https://vicky-khata.streamlit.app"
    st.markdown(f'<a href="whatsapp://send?text={share_msg}" style="background-color: #25D366; color: white; padding: 12px 20px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block;">📢 WhatsApp Share</a>', unsafe_allow_html=True)

# --- 6. KHATA APP (Using Your Secret Sauce Container) ---
elif app_mode == "💰 Khata App":
    st.markdown("<h3 style='text-align: center;'>📊 VICKY KHATA</h3>", unsafe_allow_html=True)
    
    # TERA ASLI BUTTON VIEW
    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("➕ Add"): st.session_state.choice = 'add'
        if st.button("📜 Hisab"): st.session_state.choice = 'hisab'
        if st.button("🔍 Search"): st.session_state.choice = 'src'
        if st.button("🤝 Settle"): st.session_state.choice = 'set'
        if st.button("📊 Report"): st.session_state.choice = 'rep'
        if st.button("🗑️ Delete"): st.session_state.choice = 'del'

    st.divider()
    
    # Data Fetching
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status", "User"])
    
    # Filter only current user's data
    if 'User' in df.columns:
        df = df[df['User'] == user_logged_in]

    val = st.session_state.choice

    if val == 'add':
        with st.form("a", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Party", "Shopping", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, str(amt), note, "Pending" if cat=="Udhar" else "N/A", user_logged_in])
                st.success("Saved! ✅")
                st.rerun()

    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif val == 'set':
        st.subheader("🤝 Udhar Settle (Partial Balance)")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'].astype(str) + ")"
                pick = st.selectbox("Kaunsa Udhar?", pending['disp'].tolist())
                pay = st.number_input("Kitne paise mile?", min_value=0.0)
                if st.button("SETTLE NOW"):
                    row_info = pending[pending['disp'] == pick].iloc[0]
                    # Find exact row in Google Sheet
                    all_rows = sheet.get_all_values()
                    for idx, r in enumerate(all_rows):
                        if r[0] == row_info['Date'] and r[5] == user_logged_in:
                            rem = float(r[2]) - pay
                            if rem <= 0:
                                sheet.update_cell(idx+1, 5, "Paid ✅")
                                sheet.update_cell(idx+1, 3, "0")
                            else:
                                sheet.update_cell(idx+1, 3, str(rem))
                            st.success("Balance Update Ho Gaya! 💰")
                            st.rerun()
            else: st.info("Koi pending nahi hai.")

    elif val == 'del':
        st.subheader("🗑️ Entry Delete Karein")
        if not df.empty:
            df['del_opt'] = df['Date'] + " | " + df['Category'] + " | ₹" + df['Amount']
            to_del = st.selectbox("Kaunsi entry hatani hai?", df['del_opt'].tolist())
            if st.button("CONFIRM DELETE"):
                selected_date = to_del.split(" | ")[0]
                all_rows = sheet.get_all_values()
                for i, r in enumerate(all_rows):
                    if r[0] == selected_date and r[5] == user_logged_in:
                        sheet.delete_rows(i+1)
                        st.success("Entry Deleted! 🗑️")
                        st.rerun()
        else: st.info("Kuch delete karne ke liye nahi hai.")

    elif val == 'rep':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.metric("Total Kharcha", f"₹{df['Amount'].sum():,.0f}")
            st.bar_chart(df.groupby('Category')['Amount'].sum())

    elif val == 'src':
        q = st.text_input("Kuch bhi search karein (Note/Category):")
        if q:
            res = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Vicky bhai, feature jald aayega!")
