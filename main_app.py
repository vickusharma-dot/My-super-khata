import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import streamlit.components.v1 as components

# --- GOOGLE SHEETS SETUP ---
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
    st.error(f"Sheet Error: {e}")

# --- APP CONFIG & PWA ---
st.set_page_config(page_title="Vicky Hub", layout="centered", page_icon="💰")

# --- CSS STYLE ---
st.markdown("""
    <style>
    .stButton > button {
        width: auto !important; min-width: 90px !important; height: 50px !important;
        margin: 4px 6px !important; border-radius: 10px !important;
        border: 2px solid #4CAF50 !important; font-weight: bold !important;
    }
    section.main > div.block-container { padding-top: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Secure Login")
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
                else:
                    st.error("Galat PIN! ❌")
            else:
                user_sheet.append_row([u_input, p_input])
                st.success("Account Ban Gaya!")
                st.session_state.user = u_input
                st.rerun()
        else:
            st.warning("Naam aur 4-digit PIN dalo!")
    st.stop()

# --- MAIN APP ---
user_logged_in = st.session_state.user
is_admin = (user_logged_in == "vicky786") # Secret Master Key

if st.sidebar.button("Logout 🚪"):
    st.session_state.user = None
    st.rerun()

app_mode = st.sidebar.radio("Menu", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if app_mode == "🏠 Home":
    st.title(f"Ram Ram, {user_logged_in.upper()}! 🙏")
    
    st.info("👈 **Shuru karein:** Sidebar (teen line) se 'Khata App' select karein.")
    
    # SHARE & SUPPORT SECTION
    st.markdown("---")
    st.markdown("### 🌟 Support Vicky Hub")
    st.write("Bhai, agar meri mehnat achi lagi ho toh doston ke sath share zaroor karein!")
    
    share_msg = "Bhai, ye dekh Vicky Hub! Mast digital khata app hai, tu bhi use kar: https://vicky-khata.streamlit.app"
    st.markdown(f"""
        <a href="whatsapp://send?text={share_msg}" data-action="share/whatsapp/share" 
           style="background-color: #25D366; color: white; padding: 12px 20px; 
                  text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block;">
           📢 WhatsApp par Share Karein
        </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.success("💡 **Tip:** Is app ko Home Screen par lagane ke liye browser menu (3 dots ⋮) mein 'Install' ya 'Add to Home Screen' karein!")

elif app_mode == "💰 Khata App":
    st.markdown(f"<h3 style='text-align: center;'>📊 {user_logged_in.upper()} KA KHATA</h3>", unsafe_allow_html=True)
    
    if 'choice' not in st.session_state: st.session_state.choice = 'None'

    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("➕ Add"): st.session_state.choice = 'add'
        if st.button("📜 Hisab"): st.session_state.choice = 'hisab'
        if st.button("🔍 Search"): st.session_state.choice = 'src'
        if st.button("🤝 Settle"): st.session_state.choice = 'set'
        if st.button("📊 Report"): st.session_state.choice = 'rep'
        if st.button("🗑️ Delete"): st.session_state.choice = 'del'

    st.divider()

    all_data = data_sheet.get_all_values()
    if len(all_data) > 1:
        cols = [c.strip() for c in all_data[0]]
        full_df = pd.DataFrame(all_data[1:], columns=cols)
        df = full_df if is_admin else full_df[full_df['User'] == user_logged_in]
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Note", "Status", "User"])

    val = st.session_state.choice

    if val == 'add':
        with st.form("add_form", clear_on_submit=True):
            cat = st.selectbox("Category", ["Khana", "Petrol", "Udhar", "Party", "Shopping", "Other"])
            amt = st.number_input("Amount", 0.0)
            note = st.text_input("Note")
            if st.form_submit_button("SAVE"):
                data_sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), cat, str(amt), note, "Pending" if cat=="Udhar" else "N/A", user_logged_in])
                st.success("Save ho gaya!"); st.rerun()

    elif val == 'hisab':
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif val == 'rep':
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            st.metric("TOTAL KHARCHA", f"₹{df['Amount'].sum():,.0f}")
            st.bar_chart(df.groupby('Category')['Amount'].sum())
        else: st.info("Koi data nahi hai.")

    elif val == 'del':
        if not df.empty:
            st.warning("Aakhri entry delete karein?")
            if st.button("HAAN"):
                if all_data[-1][-1] == user_logged_in:
                    data_sheet.delete_rows(len(all_data))
                    st.error("Deleted!"); st.session_state.choice = 'None'; st.rerun()
                else:
                    st.warning("Aap sirf apni sabse aakhri entry hi delete kar sakte hain.")

elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.write("Bhai, ispe kaam baaki hai... Stay tuned!")
    
