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
    SHEET_NAME = "Vicku_khata data" 
    sheet = client.open(SHEET_NAME).sheet1
except Exception as e:
    st.error("❌ Sheet Connect Nahi Hui!")

# --- CONFIG ---
st.set_page_config(page_title="Vicky's Pro Khata", layout="centered")

# CSS for better buttons
st.markdown("""<style> div.stButton > button { width: 100%; border-radius: 10px; height: 3em; background-color: #f0f2f6; font-weight: bold; } </style>""", unsafe_allow_html=True)

# Sidebar for App Selection
app_mode = st.sidebar.radio("Navigation", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title("🏠 Vicky's Digital Hub")
    st.info("Bhai, Khata chalane ke liye Sidebar se 'Khata App' select karo!")

elif app_mode == "💰 Khata App":
    st.title("💸 Vicky Khata (Full System)")
    
    # Fresh data fetch for all options
    all_rows = sheet.get_all_values()
    headers = [h.strip() for h in all_rows[0]] if all_rows else []
    df = pd.DataFrame(all_rows[1:], columns=headers) if len(all_rows) > 1 else pd.DataFrame()

    # --- MAIN BUTTON MENU ---
    col1, col2 = st.columns(2)
    
    btn1 = col1.button("➕ 1. Naya Kharcha")
    btn2 = col2.button("🤝 2. Udhar Settle")
    btn3 = col1.button("📜 3. Pura Hisab")
    btn4 = col2.button("🔍 4. Search")
    btn5 = col1.button("🗑️ 5. Delete Last")
    btn6 = col2.button("📊 6. Report & Total")

    st.divider()

    # --- LOGIC FOR EACH OPTION ---
    
    # 1. ADD ENTRY
    if btn1 or st.session_state.get('active_opt') == 'add':
        st.session_state.active_opt = 'add'
        st.subheader("📝 Naya Kharcha Add Karein")
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            cat = c1.selectbox("Category:", ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"])
            amt = c2.number_input("Amount (₹):", min_value=0.0)
            note = st.text_input("Note (Kiske liye?):")
            if st.form_submit_button("SAVE TO SHEET"):
                if amt > 0:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([now, cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                    st.success("✅ Save ho gaya!")
                    st.rerun()

    # 2. SETTLE UDHAR
    if btn2 or st.session_state.get('active_opt') == 'settle':
        st.session_state.active_opt = 'settle'
        st.subheader("🤝 Udhar Settle Karein")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'].str.strip() == 'Pending'].copy()
            if not pending.empty:
                pending['display'] = pending['Note'] + " (₹" + pending['Amount'] + ")"
                pick = st.selectbox("Kiska udhar kam karna hai?", pending['display'].tolist())
                pay = st.number_input("Kitne paise mile? (₹):", min_value=0.0)
                if st.button("SETTLE NOW"):
                    row_data = pending[pending['display'] == pick].iloc[0]
                    cell = sheet.find(row_date := row_data['Date'])
                    balance = float(row_data['Amount']) - pay
                    if balance <= 0:
                        sheet.update_cell(cell.row, 5, "Paid")
                        sheet.update_cell(cell.row, 3, 0)
                        st.success("✅ Pura Udhar Clear!")
                    else:
                        sheet.update_cell(cell.row, 3, balance)
                        st.warning(f"✅ ₹{pay} kam hue. Ab ₹{balance} baaki hain.")
                    st.rerun()
            else: st.write("Koi pending udhar nahi hai.")

    # 3. HISTORY
    if btn3 or st.session_state.get('active_opt') == 'hist':
        st.session_state.active_opt = 'hist'
        st.subheader("📜 Sabhi Transactions")
        if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)

    # 4. SEARCH
    if btn4 or st.session_state.get('active_opt') == 'search':
        st.session_state.active_opt = 'search'
        st.subheader("🔍 Khojein (Search)")
        q = st.text_input("Kya dhundna hai?")
        if q and not df.empty:
            res = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)

    # 5. DELETE
    if btn5:
        if len(all_rows) > 1:
            sheet.delete_rows(len(all_rows))
            st.error("🗑️ Aakhri entry delete ho gayi!")
            st.rerun()

    # 6. REPORT & TOTAL
    if btn6 or st.session_state.get('active_opt') == 'report':
        st.session_state.active_opt = 'report'
        st.subheader("📊 Category-wise Hisab")
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            
            # Grouping for report
            summary = df.groupby('Category')['Amount'].sum().reset_index()
            
            # Simple Display
            for _, row in summary.iterrows():
                st.write(f"🔹 **{row['Category']}:** ₹{row['Amount']}")
            
            st.divider()
            st.markdown(f"## **💰 Kul Kharcha: ₹{df['Amount'].sum()}**")
        else:
            st.write("Abhi koi data nahi hai.")

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.warning("Ye abhi band hai. 🚧")
    
