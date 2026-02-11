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

# --- 2. TERA ORIGINAL CSS (No Changes) ---
st.markdown("""
    <style>
    .stButton > button {
        width: auto !important;
        min-width: 85px !important;
        height: 45px !important;
        margin: 2px 4px !important;
        padding: 0 10px !important;
        font-size: 13px !important;
        border-radius: 8px !important;
        border: 2px solid #4CAF50 !important;
        font-weight: bold !important;
        white-space: nowrap !important;
    }
    section.main > div.block-container {
        overflow-x: hidden !important;
        padding-top: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN SYSTEM ---
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

# --- 5. HOME PAGE ---
if app_mode == "🏠 Home":
    st.title(f"Welcome {user_logged_in.upper()}! 😎")
    st.success("💡 **Tip:** 'Add to Home Screen' karein!")
    st.markdown("### 📢 Naya Kya Hai?")
    st.markdown("* 🔐 **Privacy:** Aapka data safe hai.\n* 🤝 **Full Fix:** Saare buttons ab kaam karenge.")
    st.info("👉 Sidebar se 'Khata App' chuno.")

# --- 6. KHATA APP ---
elif app_mode == "💰 Khata App":
    st.markdown("<h3 style='text-align: center;'>📊 VICKY KHATA</h3>", unsafe_allow_html=True)
    
    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("➕ Add"): st.session_state.choice = 'add'
        if st.button("📜 Hisab"): st.session_state.choice = 'hisab'
        if st.button("🔍 Search"): st.session_state.choice = 'src'
        if st.button("🤝 Settle"): st.session_state.choice = 'set'
        if st.button("📊 Report"): st.session_state.choice = 'rep'
        if st.button("🗑️ Delete"): st.session_state.choice = 'del'

    st.divider()
    
    # --- FIXED DATA LOADING ---
    raw = sheet.get_all_values()
    if len(raw) > 1:
        df = pd.DataFrame(raw[1:], columns=raw[0])
        if 'User' in df.columns:
            df = df[df['User'] == user_logged_in]
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status", "User"])

    val = st.session_state.choice

    if val == 'add':
        with st.form("a", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Party", "Shopping", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, str(amt), note, "Pending" if cat=="Udhar" else "N/A", user_logged_in])
                st.success("Saved! ✅"); st.rerun()

    elif val == 'hisab':
        if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("Khata khali hai.")

    elif val == 'src':
        st.subheader("🔍 Search")
        q = st.text_input("Note ya Category likho:")
        if q and not df.empty:
            res = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)
        elif q: st.warning("Data nahi mila.")

    elif val == 'set':
        st.subheader("🤝 Udhar Settle")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'].astype(str) + " (₹" + pending['Amount'].astype(str) + ")"
                pick = st.selectbox("Kaunsa?", pending['disp'].tolist())
                pay = st.number_input("Amount received?", min_value=0.0)
                if st.button("CONFIRM SETTLE"):
                    row_info = pending[pending['disp'] == pick].iloc[0]
                    all_r = sheet.get_all_values()
                    for i, r in enumerate(all_r):
                        if r[0] == row_info['Date'] and r[5] == user_logged_in:
                            rem = float(r[2]) - pay
                            if rem <= 0:
                                sheet.update_cell(i+1, 5, "Paid ✅")
                                sheet.update_cell(i+1, 3, "0")
                            else:
                                sheet.update_cell(i+1, 3, str(rem))
                            st.success("Updated!"); st.rerun()
            else: st.info("Koi Udhar Pending nahi hai.")
        else: st.info("Abhi koi data nahi hai.")

    elif val == 'rep':
        st.subheader("📊 Report")
        if not df.empty and 'Amount' in df.columns:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.metric("Total Kharcha", f"₹{df['Amount'].sum():,.0f}")
            st.bar_chart(df.groupby('Category')['Amount'].sum())
        else: st.warning("Report ke liye data nahi mila.")

    elif val == 'del':
        st.subheader("🗑️ Delete Entry")
        if not df.empty:
            df['del_opt'] = df['Date'].astype(str) + " | " + df['Category'].astype(str) + " | ₹" + df['Amount'].astype(str)
            to_del = st.selectbox("Select to delete:", df['del_opt'].tolist())
            if st.button("DELETE NOW"):
                sel_date = to_del.split(" | ")[0]
                all_r = sheet.get_all_values()
                for i, r in enumerate(all_r):
                    if r[0] == sel_date and r[5] == user_logged_in:
                        sheet.delete_rows(i+1)
                        st.success("Deleted!"); st.rerun()
        else: st.info("Kuch nahi hai delete karne ko.")

elif app_mode == "🏧 Digital ATM":
    st.write("Jald aa raha hai!")
    
