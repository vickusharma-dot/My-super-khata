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
        note = st.text_input("Kiske liye? (Note likhna zaroori hai):")
        
        if st.button("💾 SAVE TO CLOUD", use_container_width=True):
            if amt > 0:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Date, Category, Amount, Note, Status
                sheet.append_row([now, cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                st.success(f"✅ ₹{amt} save ho gaya!")
                st.rerun()

    with col2:
        st.markdown("### **🤝 Udhar Settle Karein**")
        raw_rows = sheet.get_all_values()
        if len(raw_rows) > 1:
            df_all = pd.DataFrame(raw_rows[1:], columns=raw_rows[0])
            # Pending filter (Status column)
            pending_df = df_all[df_all['Status'] == 'Pending'].copy()
            
            if not pending_df.empty:
                # Identification ke liye Note aur Date dono use karenge
                pending_df['display_name'] = pending_df['Note'] + " (₹" + pending_df['Amount'] + ") - " + pending_df['Date']
                
                selected_item = st.selectbox("Kaunsa udhar khatam hua?", pending_df['display_name'].tolist())
                
                if st.button("✅ MARK AS PAID", use_container_width=True):
                    # Date se exact row dhundna sabse safe hai
                    selected_date = selected_item.split(" - ")[-1]
                    cell = sheet.find(selected_date)
                    
                    if cell:
                        sheet.update_cell(cell.row, 5, "Paid") # Status Column
                        sheet.update_cell(cell.row, 3, "0")    # Amount 0
                        st.success("Bhai, hisab clear ho gaya!")
                        st.rerun()
            else:
                st.info("Abhi koi pending udhar nahi hai. 😎")
        else:
            st.write("Data loading...")

# --- TAB 2: HISTORY ---
with tab2:
    st.markdown("### **🔍 Pura Hisab aur Khoj**")
    if len(raw_rows) > 1:
        df_hist = pd.DataFrame(raw_rows[1:], columns=raw_rows[0])
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Aakhri Entry Delete"):
            sheet.delete_rows(len(raw_rows))
            st.warning("Entry deleted!")
            st.rerun()

# --- TAB 3: REPORTS ---
with tab3:
    st.markdown("### **📊 Summary**")
    if len(raw_rows) > 1:
        df_rep = pd.DataFrame(raw_rows[1:], columns=raw_rows[0])
        df_rep['Amount'] = pd.to_numeric(df_rep['Amount'], errors='coerce').fillna(0)
        st.metric("TOTAL KHARCHA", f"₹{df_rep['Amount'].sum()}")
        st.bar_chart(df_rep.groupby('Category')['Amount'].sum())
