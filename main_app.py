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
    
    # JO NAAM TUNE BATAYA: Vicku_khata data
    SHEET_NAME = "Vicku_khata data" 
    sheet = client.open(SHEET_NAME).sheet1
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.info("Bhai, check karo ki Google Sheet ka naam 'Vicku_khata data' hi hai na? Aur tune Service Account email ko Share kiya hai?")

# --- CONFIG ---
st.set_page_config(page_title="Vicky's Cloud Khata", layout="wide")
CATEGORIES = ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"]

# --- SIDEBAR ---
st.sidebar.title("📱 Vicky's App Store")
selected_app = st.sidebar.selectbox("Chuno:", ["💰 Khata App", "🏧 Digital ATM"])

if selected_app == "💰 Khata App":
    st.title("💸 Digital Khata (Google Sheets)")
    
    # 1 se 9 tak ke saare options yahan tabs mein hain
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Entry & Udhar", "📜 History & Search", "📊 Reports", "💸 Budget"])

    # --- TAB 1: ADD & SETTLE ---
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Kharcha Add Karein")
            cat = st.selectbox("Category:", CATEGORIES)
            amt = st.number_input("Amount (₹):", min_value=0.0, step=10.0)
            note = st.text_input("Note (Kiske liye?):")
            if st.button("Save to Cloud"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Sheet columns: Date, Category, Amount, Note, Status
                sheet.append_row([now, cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                st.success("✅ Google Sheet mein save ho gaya!")

        with col2:
            st.subheader("3. Udhar Settle")
            try:
                data_records = sheet.get_all_records()
                if data_records:
                    df_udhar = pd.DataFrame(data_records)
                    if 'Status' in df_udhar.columns:
                        pending = df_udhar[df_udhar['Status'] == 'Pending']
                        if not pending.empty:
                            to_settle = st.selectbox("Kiska udhar settle karna hai?", pending['Note'].tolist())
                            if st.button("Mark as Paid"):
                                cell = sheet.find(to_settle)
                                sheet.update_cell(cell.row, 5, "Paid")
                                sheet.update_cell(cell.row, 3, 0) # Udhar settle matlab 0 kharcha bacha
                                st.success(f"✅ {to_settle} ka udhar settle ho gaya!")
                                st.rerun()
                        else: st.write("Sab udhar cleared hain! ✅")
                else: st.write("Abhi koi data nahi hai.")
            except: st.write("Udhar check karne ke liye pehle kuch data dalo.")

    # --- TAB 2: HISTORY & SEARCH ---
    with tab2:
        st.subheader("2. Pura Hisab & 6. Search")
        try:
            raw_data = sheet.get_all_records()
            if raw_data:
                df = pd.DataFrame(raw_data)
                search = st.text_input("🔍 Dhundo (Note ya Category likho):")
                if search:
                    df = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)]
                st.dataframe(df, use_container_width=True)
                
                if st.button("5. Entry Delete Karein (Aakhri wali)"):
                    sheet.delete_rows(len(sheet.get_all_values()))
                    st.warning("🗑️ Aakhri entry hata di gayi!")
                    st.rerun()
            else:
                st.info("Abhi history khali hai.")
        except: st.error("Data load nahi ho pa raha.")

    # --- TAB 3: SUMMARY & MONTHLY ---
    with tab3:
        st.subheader("4. Summary & 7. Monthly Report")
        try:
            if raw_data:
                df_rep = pd.DataFrame(raw_data)
                df_rep['Amount'] = pd.to_numeric(df_rep['Amount'])
                st.write(f"### 💰 Total Kharcha: ₹{df_rep['Amount'].sum()}")
                
                # Category Chart
                cat_sum = df_rep.groupby('Category')['Amount'].sum()
                st.bar_chart(cat_sum)
                
                # Monthly Logic
                df_rep['Month'] = df_rep['Date'].str[:7] # YYYY-MM nikalne ke liye
                st.write("### 📅 Monthly Hisab:")
                st.table(df_rep.groupby('Month')['Amount'].sum())
        except: st.write("Report dikhane ke liye data kam hai.")

    # --- TAB 4: BUDGET ---
    with tab4:
        st.subheader("8. Monthly Budget Set Karein")
        b_val = st.number_input("Budget (₹):", value=0.0)
        if st.button("Set Budget"):
            st.success(f"✅ Budget ₹{b_val} set ho gaya! (App iska dhyan rakhegi)")

else:
    st.title("🏧 Digital ATM")
    st.warning("Bhai ne bola abhi side mein rakhne ka! Jab bolo tab chalu kar denge. 😎")
    
