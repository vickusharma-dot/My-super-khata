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
    st.error("❌ Sheet connection error!")

# --- STYLE ---
st.set_page_config(page_title="Vicky's Hub", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>💰 VICKY DIGITAL KHATA</h1>", unsafe_allow_html=True)
st.divider()

tab1, tab2, tab3 = st.tabs(["➕ Nayi Entry", "📜 Pura Hisab & Khoj", "📊 Report & Summary"])

# --- TAB 1: ADD & SETTLE ---
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### **📥 Naya Kharcha Add Karein**")
        cat = st.selectbox("Category Chuno:", ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"])
        amt = st.number_input("Kitne Paise (₹):", min_value=0.0, step=10.0)
        note = st.text_input("Note (Kiske liye?):")
        
        if st.button("💾 SAVE TO CLOUD", use_container_width=True):
            if amt > 0:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Order: Date, Category, Amount, Note, Status
                sheet.append_row([now, cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                st.success(f"✅ ₹{amt} save ho gaya!")
                st.rerun()

    with col2:
        st.markdown("### **🤝 Udhar Settle Karein**")
        all_data = sheet.get_all_values()
        if len(all_data) > 1:
            # Headers ko saaf kar rahe hain (spaces hata rahe hain)
            headers = [h.strip() for h in all_data[0]]
            df_all = pd.DataFrame(all_data[1:], columns=headers)
            
            # Pakka kar rahe hain ki 'Status' column maujood hai
            if 'Status' in df_all.columns:
                pending_df = df_all[df_all['Status'].str.strip() == 'Pending'].copy()
                
                if not pending_df.empty:
                    # Dropdown mein Note ya Date dikhao
                    pending_df['display'] = pending_df['Note'].replace('', 'No Name') + " (₹" + pending_df['Amount'] + ") - " + pending_df['Date']
                    selected_u = st.selectbox("Kiska udhar khatam hua?", pending_df['display'].tolist())
                    
                    if st.button("✅ MARK AS PAID", use_container_width=True):
                        # Date se row dhoondo
                        row_date = selected_u.split(" - ")[-1]
                        cell = sheet.find(row_date)
                        if cell:
                            sheet.update_cell(cell.row, 5, "Paid") # Status Column
                            sheet.update_cell(cell.row, 3, "0")    # Amount 0
                            st.success("Bhai, hisab clear!")
                            st.rerun()
                else:
                    st.success("Sab udhar clear hain! 😎")
            else:
                st.error("Sheet mein 'Status' column nahi mil raha. Headers check karo.")
        else:
            st.write("Abhi koi data nahi hai.")

# --- TAB 2: HISTORY ---
with tab2:
    st.markdown("### **🔍 Sabhi Transactions**")
    if len(all_data) > 1:
        st.dataframe(pd.DataFrame(all_data[1:], columns=headers), use_container_width=True, hide_index=True)

# --- TAB 3: REPORTS ---
with tab3:
    st.markdown("### **📊 Summary**")
    if len(all_data) > 1:
        df_rep = pd.DataFrame(all_data[1:], columns=headers)
        df_rep['Amount'] = pd.to_numeric(df_rep['Amount'], errors='coerce').fillna(0)
        st.metric("TOTAL KHARCHA", f"₹{df_rep['Amount'].sum()}")
        
