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
    st.error("Sheet Error!")

st.set_page_config(page_title="Vicky Hub", layout="centered")

# --- CSS FOR HORIZONTAL BUTTONS ---
st.markdown("""
    <style>
    .stButton > button {
        width: auto !important; min-width: 95px !important; height: 50px !important;
        margin: 4px 6px !important; padding: 0 12px !important;
        font-size: 14px !important; border-radius: 10px !important;
        border: 2px solid #4CAF50 !important; font-weight: bold !important;
        white-space: nowrap !important;
    }
    section.main > div.block-container { overflow-x: hidden !important; padding-top: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
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
                else: st.error("Wrong PIN!")
            else:
                user_sheet.append_row([u_input, p_input])
                st.session_state.user = u_input
                st.rerun()
    st.stop()

# --- APP NAVIGATION ---
user_logged_in = st.session_state.user
if 'choice' not in st.session_state: st.session_state.choice = 'None'
app_mode = st.sidebar.radio("Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title(f"Welcome {user_logged_in.upper()}! 😎")
    st.info("Bhai, Sidebar se 'Khata App' select karo.")

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
    
    # Load Data
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame()
    if not df.empty:
        df = df[df['User'] == user_logged_in]

    val = st.session_state.choice

    if val == 'add':
        with st.form("a", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Party", "Shopping", "Safar", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, amt, note, "Pending" if cat=="Udhar" else "N/A", user_logged_in])
                st.success("Saved!"); st.rerun()

    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif val == 'set':
        st.subheader("🤝 Udhar Settle (Partial)")
        pending = df[df['Status'] == 'Pending'].copy()
        if not pending.empty:
            pending['options'] = pending['Note'] + " (₹" + pending['Amount'] + ")"
            choice = st.selectbox("Kaunsa Udhar?", pending['options'].tolist())
            pay = st.number_input("Kitne wapas mile?", min_value=0.0)
            if st.button("UPDATE BALANCE"):
                row_data = pending[pending['options'] == choice].iloc[0]
                all_rows = sheet.get_all_values()
                # Find row index based on Date and User
                for i, r in enumerate(all_rows):
                    if r[0] == row_data['Date'] and r[5] == user_logged_in:
                        new_amt = float(row_data['Amount']) - pay
                        if new_amt <= 0:
                            sheet.update_cell(i+1, 5, "Paid ✅")
                            sheet.update_cell(i+1, 3, 0)
                        else:
                            sheet.update_cell(i+1, 3, new_amt)
                            sheet.update_cell(i+1, 5, "Pending")
                        st.success("Updated!"); st.rerun()
        else: st.info("No Pending Udhar.")

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
                        st.success("Deleted!"); st.rerun()
        else: st.info("No data to delete.")

    elif val == 'rep':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.metric("Total Kharcha", f"₹{df['Amount'].sum():,.0f}")
            st.bar_chart(df.groupby('Category')['Amount'].sum())

    elif val == 'src':
        q = st.text_input("Search (Note/Category):")
        if q:
            res = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)

elif app_mode == "🏧 Digital ATM":
    st.write("Jald aa raha hai!")
