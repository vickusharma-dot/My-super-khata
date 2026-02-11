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
    main_sheet = client.open("Vicku_khata data")
    sheet = main_sheet.sheet1
    try:
        user_sheet = main_sheet.worksheet("Users")
    except:
        user_sheet = main_sheet.add_worksheet(title="Users", rows="100", cols="2")
        user_sheet.append_row(["Username", "PIN"])
except Exception as e:
    st.error("Sheet Error! Check Secrets.")

st.set_page_config(page_title="Vicky Hub", layout="centered", page_icon="💰")

# --- CUSTOM CSS (Asli Secret Sauce) ---
st.markdown("""
    <style>
    .stButton > button {
        width: auto !important; min-width: 95px !important; height: 50px !important;
        margin: 4px 6px !important; padding: 0 12px !important;
        font-size: 14px !important; border-radius: 10px !important;
        border: 2px solid #4CAF50 !important; font-weight: bold !important;
        white-space: nowrap !important; color: #4CAF50 !important;
    }
    .stButton > button:hover { background-color: #4CAF50 !important; color: white !important; }
    section.main > div.block-container { overflow-x: hidden !important; padding-top: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
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
    st.stop()

# --- MAIN APP ---
user_logged_in = st.session_state.user
is_admin = (user_logged_in == "vicky786")

if 'choice' not in st.session_state: st.session_state.choice = 'None'

app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])
if st.sidebar.button("Logout 🚪"):
    st.session_state.user = None
    st.rerun()

if app_mode == "🏠 Home":
    st.title(f"Welcome, {user_logged_in.upper()}! 😎")
    st.success("💡 **Tip:** Is app ko Home Screen par lagane ke liye browser menu (3 dots ⋮) mein 'Install' ya 'Add to Home Screen' karein!")
    st.info("👉 Sidebar se 'Khata App' chuno apna hisab dekhne ke liye.")
    
    st.markdown("---")
    st.markdown("### 🌟 Support Vicky Hub")
    st.write("Bhai, agar meri ye mehnat achi lagi ho, toh apne doston ke sath share zaroor karein! Aapka support hi meri taqat hai.")
    
    share_msg = "Bhai, ye dekh Vicky Hub! Mast digital khata app: https://vicky-khata.streamlit.app"
    st.markdown(f'<a href="whatsapp://send?text={share_msg}" style="background-color: #25D366; color: white; padding: 12px 20px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block;">📢 WhatsApp Share</a>', unsafe_allow_html=True)

elif app_mode == "💰 Khata App":
    st.markdown(f"<h3 style='text-align: center;'>📊 {user_logged_in.upper()} KHATA</h3>", unsafe_allow_html=True)
    
    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("➕ Add"): st.session_state.choice = 'add'
        if st.button("📜 Hisab"): st.session_state.choice = 'hisab'
        if st.button("🔍 Search"): st.session_state.choice = 'src'
        if st.button("🤝 Settle"): st.session_state.choice = 'set'
        if st.button("📊 Report"): st.session_state.choice = 'rep'
        if st.button("🗑️ Delete"): st.session_state.choice = 'del'

    st.divider()
    
    val = st.session_state.choice
    all_data = sheet.get_all_values()
    if len(all_data) > 1:
        full_df = pd.DataFrame(all_data[1:], columns=all_data[0])
        df = full_df if is_admin else full_df[full_df['User'] == user_logged_in]
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status", "User"])

    if val == 'add':
        with st.form("a", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Party", "Shopping", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, amt, note, "Pending" if cat=="Udhar" else "N/A", user_logged_in])
                st.success("Saved!")
                st.rerun()

    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif val == 'set':
        st.subheader("🤝 Partial Settle (Paisa Vasool)")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'].astype(str) + ")"
                pick = st.selectbox("Kiska udhar?", pending['disp'].tolist())
                pay = st.number_input("Kitne paise mile?", min_value=0.0)
                
                if st.button("UPDATE BALANCE"):
                    row_info = pending[pending['disp'] == pick].iloc[0]
                    # Find correct row in Google Sheet
                    all_rows = sheet.get_all_values()
                    row_idx = -1
                    for idx, r in enumerate(all_rows):
                        if r[0] == row_info['Date'] and r[5] == user_logged_in:
                            row_idx = idx + 1
                            break
                    
                    if row_idx != -1:
                        old_amt = float(row_info['Amount'])
                        rem = old_amt - pay
                        if rem <= 0:
                            sheet.update_cell(row_idx, 5, "Paid ✅")
                            sheet.update_cell(row_idx, 3, 0)
                            st.success("Poora Udhar Khatam!")
                        else:
                            sheet.update_cell(row_idx, 3, rem)
                            sheet.update_cell(row_idx, 5, f"Partially Paid")
                            st.warning(f"₹{rem} abhi bhi baki hain!")
                        st.rerun()
            else: st.info("Koi Pending Udhar nahi hai.")

    elif val == 'rep':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.metric("TOTAL KHARCHA", f"₹{df['Amount'].sum():,.0f}")
            st.bar_chart(df.groupby('Category')['Amount'].sum())

    elif val == 'src':
        query = st.text_input("Search Note ya Category:")
        if query:
            res = df[df.apply(lambda r: query.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)

    elif val == 'del':
        if not df.empty:
            st.warning("Aakhri entry delete ho jayegi. Pakka?")
            if st.button("HAAN, DELETE KARO"):
                all_rows = sheet.get_all_values()
                if all_rows[-1][5] == user_logged_in:
                    sheet.delete_rows(len(all_rows))
                    st.success("Deleted!")
                    st.rerun()
                else: st.error("Aap sirf apni entry delete kar sakte hain!")

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Vicky bhai, kaam chal raha hai... Jald aayega!")
