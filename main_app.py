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
    st.error(f"Sheet Connect Nahi Hui: {e}")

# --- APP CONFIG ---
st.set_page_config(page_title="Vicky Hub", layout="centered")

# --- TERA CSS (LATEST BUTTON STYLE) ---
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

if 'choice' not in st.session_state:
    st.session_state.choice = 'None'

# --- SIDEBAR MENU ---
app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title("Welcome Vicky! 😎")
    st.info("Bhai, Sidebar se app chuno.")

elif app_mode == "💰 Khata App":
    st.markdown("<h3 style='text-align: center;'>📊 VICKY KHATA</h3>", unsafe_allow_html=True)
    
    # --- TERA WORKING HORIZONTAL CONTAINER ---
    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("➕ Add", key="btn_add"): st.session_state.choice = 'add'
        if st.button("📜 Hisab", key="btn_hisab"): st.session_state.choice = 'hisab'
        if st.button("🔍 Search", key="btn_src"): st.session_state.choice = 'src'
        if st.button("🤝 Settle", key="btn_set"): st.session_state.choice = 'set'
        if st.button("📊 Report", key="btn_rep"): st.session_state.choice = 'rep'
        if st.button("🗑️ Delete", key="btn_del"): st.session_state.choice = 'del'

    st.divider()
    
    # Safe Data Fetching
    data_values = sheet.get_all_values()
    if len(data_values) > 1:
        df = pd.DataFrame(data_values[1:], columns=data_values[0])
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status"])

    val = st.session_state.choice

    # 1. ADD ENTRY
    if val == 'add':
        with st.form("a", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Safar", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, str(amt), note, "Pending" if cat=="Udhar" else "N/A"])
                st.success("Entry Saved!"); st.rerun()

    # 2. HISAB (Full Table)
    elif val == 'hisab':
        st.subheader("📜 Pura Hisab")
        st.dataframe(df, use_container_width=True, hide_index=True)

    # 3. SEARCH (Working)
    elif val == 'src':
        st.subheader("🔍 Search Result")
        search_q = st.text_input("Naam ya Category likho...")
        if search_q:
            res = df[df.apply(lambda r: search_q.lower() in r.astype(str).str.lower().values, axis=1)]
            if not res.empty: st.dataframe(res, use_container_width=True, hide_index=True)
            else: st.warning("Kuch nahi mila!")

    # 4. SETTLE (Update Logic)
    elif val == 'set':
        st.subheader("🤝 Udhar Settle")
        if not df.empty and "Status" in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'].astype(str) + ")"
                pick = st.selectbox("Kiska settle karna hai?", pending['disp'].tolist())
                pay = st.number_input("Kitne paise mile?", 0.0)
                if st.button("SETTLE NOW"):
                    match = df[df['Note'] + " (₹" + df['Amount'].astype(str) + ")" == pick]
                    row_idx = match.index[0] + 2
                    rem = float(match.iloc[0]['Amount']) - pay
                    if rem <= 0:
                        sheet.update_cell(row_idx, 5, "Paid")
                        sheet.update_cell(row_idx, 3, "0")
                    else:
                        sheet.update_cell(row_idx, 3, str(rem))
                    st.success("Update Ho Gaya!"); st.rerun()
            else: st.info("Koi pending nahi hai.")

    # 5. REPORT (FIXED AMOUNT ERROR)
    elif val == 'rep':
        st.subheader("📊 Summary Report")
        if not df.empty:
            # Amount ko number mein badalne ka ilaaj taaki Report kaam kare
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            summary = df.groupby('Category')['Amount'].sum()
            for k, v in summary.items():
                if v > 0: st.write(f"🔹 **{k}:** ₹{v:,.0f}")
            st.divider()
            st.markdown(f"## **Total Kharcha: ₹{df['Amount'].sum():,.0f}**")
        else: st.info("Data nahi hai bhai!")

    # 6. DELETE (Working)
    elif val == 'del':
        st.subheader("🗑️ Delete Last")
        if len(data_values) > 1:
            st.warning(f"Kya aap is entry ko hatana chahte hain? \n\n {data_values[-1]}")
            if st.button("HAAN, DELETE KARO"):
                sheet.delete_rows(len(data_values))
                st.error("Entry Deleted!"); st.session_state.choice = 'None'; st.rerun()

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Bhai, ye feature jald aayega!")
    
