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

st.set_page_config(page_title="Vicky Hub", layout="centered")

# --- TERA WAHI CSS (LAYOUT NAHI HILEGA) ---
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

# --- SIDEBAR ---
app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title("Welcome Vicky! 😎")
    st.info("Bhai, Sidebar se app chuno.")

elif app_mode == "💰 Khata App":
    st.markdown("<h3 style='text-align: center;'>📊 VICKY KHATA</h3>", unsafe_allow_html=True)
    
    # TERA HORIZONTAL CONTAINER (BILKUL SAME)
    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("➕ Add", key="btn_add"): st.session_state.choice = 'add'
        if st.button("📜 Hisab", key="btn_hisab"): st.session_state.choice = 'hisab'
        if st.button("🔍 Search", key="btn_src"): st.session_state.choice = 'src'
        if st.button("🤝 Settle", key="btn_set"): st.session_state.choice = 'set'
        if st.button("📊 Report", key="btn_rep"): st.session_state.choice = 'rep'
        if st.button("🗑️ Delete", key="btn_del"): st.session_state.choice = 'del'

    st.divider()
    
    # Safe Data Loading (Error Fix)
    all_values = sheet.get_all_values()
    if len(all_values) > 1:
        df = pd.DataFrame(all_values[1:], columns=all_values[0])
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status"])

    val = st.session_state.choice

    # 1. ADD
    if val == 'add':
        with st.form("a", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Safar", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, str(amt), note, "Pending" if cat=="Udhar" else "N/A"])
                st.success("Entry Saved!"); st.rerun()

    # 2. HISAB
    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)

    # 3. SEARCH (WORKING)
    elif val == 'src':
        search_q = st.text_input("Naam ya Category likho...")
        if search_q:
            filtered_df = df[df.apply(lambda row: search_q.lower() in row.astype(str).str.lower().values, axis=1)]
            st.dataframe(filtered_df, use_container_width=True)

    # 4. SETTLE
    elif val == 'set':
        if not df.empty and "Status" in df.columns:
            pending = df[df['Status'] == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'] + ")"
                pick = st.selectbox("Kiska settle karna hai?", pending['disp'].tolist())
                pay = st.number_input("Kitne mile?", 0.0)
                if st.button("CONFIRM SETTLE"):
                    row_idx = df[df['Note'] + " (₹" + df['Amount'] + ")" == pick].index[0] + 2
                    rem = float(df.iloc[row_idx-2]['Amount']) - pay
                    if rem <= 0:
                        sheet.update_cell(row_idx, 5, "Paid")
                        sheet.update_cell(row_idx, 3, "0")
                    else:
                        sheet.update_cell(row_idx, 3, str(rem))
                    st.success("Done!"); st.rerun()
            else: st.info("Sab clear hai!")

    # 5. REPORT (FIXED KEYERROR)
    elif val == 'rep':
        if not df.empty:
            # Amount ko number mein badalne ka pakka ilaaj (Error nahi aayega)
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            
            # Category wise total
            summary = df.groupby('Category')['Amount'].sum()
            
            st.subheader("📊 Kharcha Report")
            for k, v in summary.items():
                if v > 0:
                    st.write(f"🔹 **{k}:** ₹{v:,.0f}")
            
            st.divider()
            # Grand Total
            st.markdown(f"## **Total Kharcha: ₹{df['Amount'].sum():,.0f}**")
        else:
            st.info("Bhai, abhi sheet mein koi data nahi hai!")
            

    # 6. DELETE (WORKING)
    elif val == 'del':
        if len(all_values) > 1:
            st.warning(f"Delete Last Entry: {all_values[-1]}")
            if st.button("DELETE PERMANENTLY"):
                sheet.delete_rows(len(all_values))
                st.error("Entry Gayab!"); st.session_state.choice = 'None'; st.rerun()

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Jald aa raha hai...")
    
