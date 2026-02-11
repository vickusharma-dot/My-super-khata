import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# --- 1. GOOGLE SHEETS SETUP ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Vicku_khata data").sheet1
except:
    st.error("Sheet Error! Connection check karo.")

st.set_page_config(page_title="Vicky Hub", layout="centered")

# --- 2. TERA PASANDIDA BUTTON CSS ---
st.markdown("""
    <style>
    .stButton > button {
        width: 100% !important;
        height: 60px !important;
        margin-bottom: 10px !important;
        font-size: 16px !important;
        border-radius: 12px !important;
        border: 2px solid #4CAF50 !important;
        font-weight: bold !important;
    }
    [data-testid="column"] { padding: 5px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'choice' not in st.session_state:
    st.session_state.choice = 'None'

# --- 3. SIDEBAR MENU ---
app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title("Welcome Vicky! 😎")
    st.info("Bhai, Sidebar se app chuno.")

elif app_mode == "💰 Khata App":
    st.markdown("<h3 style='text-align: center;'>📊 VICKY KHATA</h3>", unsafe_allow_html=True)
    
    # --- YE HAI TERA 2-COLUMN GRID VIEW (Fixed) ---
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add", key="btn_add"): st.session_state.choice = 'add'
        if st.button("🔍 Search", key="btn_src"): st.session_state.choice = 'src'
        if st.button("📊 Report", key="btn_rep"): st.session_state.choice = 'rep'
    with c2:
        if st.button("📜 Hisab", key="btn_hisab"): st.session_state.choice = 'hisab'
        if st.button("🤝 Settle", key="btn_set"): st.session_state.choice = 'set'
        if st.button("🗑️ Delete", key="btn_del"): st.session_state.choice = 'del'

    st.divider()
    
    # --- ERROR-FREE DATA LOADING ---
    data = sheet.get_all_values()
    # Yahan hum check kar rahe hain ki data hai ya nahi (KeyError Fix)
    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status"])

    val = st.session_state.choice

    if val == 'add':
        with st.form("a", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Safar", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, str(amt), note, "Pending" if cat=="Udhar" else "N/A"])
                st.success("Saved!")
                st.rerun()

    elif val == 'rep':
        # Report logic with Safety Check
        if not df.empty and 'Amount' in df.columns:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            summary = df.groupby('Category')['Amount'].sum()
            for k, v in summary.items():
                if v > 0: st.write(f"🔹 **{k}:** ₹{v:,.0f}")
            st.markdown(f"## **Total: ₹{df['Amount'].sum():,.0f}**")
        else:
            st.warning("Abhi koi data nahi hai report ke liye.")

    elif val == 'hisab':
        if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("Khata khali hai.")

    elif val == 'set':
        st.subheader("🤝 Udhar Settle")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'].astype(str) + ")"
                pick = st.selectbox("Kiska udhar?", pending['disp'].tolist())
                pay = st.number_input("Kitne paise mile?", min_value=0.0)
                if st.button("SETTLE NOW"):
                    row_info = pending[pending['disp'] == pick].iloc[0]
                    cell = sheet.find(row_info['Date'])
                    rem = float(row_info['Amount']) - pay
                    if rem <= 0:
                        sheet.update_cell(cell.row, 5, "Paid")
                        sheet.update_cell(cell.row, 3, "0")
                    else:
                        sheet.update_cell(cell.row, 3, str(rem))
                    st.success("Update Ho Gaya!")
                    st.rerun()
            else: st.info("Koi pending nahi hai.")

    elif val == 'src':
        q = st.text_input("Kya search karna hai?")
        if q and not df.empty:
            res = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res)

    elif val == 'del':
        st.subheader("🗑️ Entry Delete")
        if not df.empty:
            df['del_opt'] = df['Date'] + " | " + df['Category'] + " | ₹" + df['Amount']
            to_del = st.selectbox("Select entry:", df['del_opt'].tolist())
            if st.button("DELETE NOW"):
                sel_date = to_del.split(" | ")[0]
                cell = sheet.find(sel_date)
                sheet.delete_rows(cell.row)
                st.success("Deleted!")
                st.rerun()

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Bhai, feature jald aayega!")
