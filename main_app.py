import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# --- 1. SHEET CONNECTION (Super Safe) ---
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
except Exception:
    st.error("Sheet Connection Error! Check Secrets.")
    st.stop()

st.set_page_config(page_title="Vicky Hub", layout="centered", page_icon="💰")

# --- 2. TERA ORIGINAL BUTTON STYLE (No Changes) ---
st.markdown("""
    <style>
    .stButton > button {
        width: 100% !important;
        height: 60px !important;
        margin-bottom: 10px !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        border: 2px solid #4CAF50 !important;
        font-weight: bold !important;
        background-color: white !important;
        color: #4CAF50 !important;
    }
    /* Mobile columns fix */
    [data-testid="column"] { padding: 5px !important; }
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
                else: st.error("Wrong PIN!")
            else:
                user_sheet.append_row([u_input, p_input])
                st.session_state.user = u_input
                st.rerun()
    st.stop()

# --- 4. NAVIGATION ---
user_logged_in = st.session_state.user
if 'choice' not in st.session_state: st.session_state.choice = 'None'
app_mode = st.sidebar.radio("Main Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

# --- 5. HOME PAGE (Wahi lines jo pehle thin) ---
if app_mode == "🏠 Home":
    st.title(f"Ram Ram, {user_logged_in.upper()}! 🙏")
    st.success("💡 **Tip:** Browser menu (3 dots) se 'Add to Home Screen' karke app banayein!")
    st.markdown("### 📢 Naya Kya Hai?")
    st.markdown("* 🔐 **Safety:** Aapka data PIN se lock hai.\n* 🤝 **Partial Settle:** Udhar wapsi ka hisab fix hai.")
    st.info("👉 Sidebar se 'Khata App' chuno.")
    share_msg = "Bhai, ye dekh Vicky Hub! Mast digital khata app: https://vicky-khata.streamlit.app"
    st.markdown(f'<a href="whatsapp://send?text={share_msg}" style="background-color: #25D366; color: white; padding: 12px 20px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block;">📢 WhatsApp Share</a>', unsafe_allow_html=True)

# --- 6. KHATA APP (Tera Original 2-Column Grid) ---
elif app_mode == "💰 Khata App":
    st.markdown("<h3 style='text-align: center;'>📊 VICKU KA KHATA</h3>", unsafe_allow_html=True)
    
    # Grid layout as per your video/screenshots
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add"): st.session_state.choice = 'add'
        if st.button("🔍 Search"): st.session_state.choice = 'src'
        if st.button("📊 Report"): st.session_state.choice = 'rep'
    with c2:
        if st.button("📜 Hisab"): st.session_state.choice = 'hisab'
        if st.button("🤝 Settle"): st.session_state.choice = 'set'
        if st.button("🗑️ Delete"): st.session_state.choice = 'del'

    st.divider()
    
    # --- ERROR-FREE DATA LOADING ---
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
                st.success("Saved!"); st.rerun()

    elif val == 'hisab':
        if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("Hisab khali hai.")

    elif val == 'rep':
        if not df.empty and 'Amount' in df.columns:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.metric("Total Kharcha", f"₹{df['Amount'].sum():,.0f}")
            st.bar_chart(df.groupby('Category')['Amount'].sum())
        else: st.warning("Report ke liye data chahiye.")

    elif val == 'set':
        st.subheader("🤝 Udhar Settle")
        if not df.empty and 'Status' in df.columns:
            pending = df[df['Status'] == 'Pending'].copy()
            if not pending.empty:
                pending['disp'] = pending['Note'] + " (₹" + pending['Amount'] + ")"
                pick = st.selectbox("Kaunsa?", pending['disp'].tolist())
                pay = st.number_input("Kitne mile?", min_value=0.0)
                if st.button("SETTLE NOW"):
                    row_info = pending[pending['disp'] == pick].iloc[0]
                    all_data = sheet.get_all_values()
                    for i, r in enumerate(all_data):
                        if r[0] == row_info['Date'] and r[5] == user_logged_in:
                            rem = float(r[2]) - pay
                            if rem <= 0:
                                sheet.update_cell(i+1, 5, "Paid ✅")
                                sheet.update_cell(i+1, 3, "0")
                            else:
                                sheet.update_cell(i+1, 3, str(rem))
                            st.success("Balance Update!"); st.rerun()
            else: st.info("Koi Udhar pending nahi hai.")

    elif val == 'del':
        st.subheader("🗑️ Delete Entry")
        if not df.empty:
            df['del_opt'] = df['Date'] + " | " + df['Category'] + " | ₹" + df['Amount']
            to_del = st.selectbox("Select:", df['del_opt'].tolist())
            if st.button("DELETE"):
                sel_date = to_del.split(" | ")[0]
                all_data = sheet.get_all_values()
                for i, r in enumerate(all_data):
                    if r[0] == sel_date and r[5] == user_logged_in:
                        sheet.delete_rows(i+1)
                        st.success("Deleted!"); st.rerun()
        else: st.info("Kuch nahi hai delete karne ko.")

    elif val == 'src':
        q = st.text_input("Note ya Category search karein:")
        if q:
            res = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)

elif app_mode == "🏧 Digital ATM":
    st.write("Jald aa raha hai!")
