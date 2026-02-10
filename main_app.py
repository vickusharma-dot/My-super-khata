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
    st.error(f"❌ Sheet Connection Error!")

# --- CONFIG ---
st.set_page_config(page_title="Vicky's Hub", layout="wide")
CATEGORIES = ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"]

# --- APP UI ---
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>💰 VICKY DIGITAL KHATA</h1>", unsafe_allow_html=True)
st.divider()

# Main Menu in Tabs
tab1, tab2, tab3 = st.tabs(["➕ Nayi Entry", "📜 Pura Hisab & Khoj", "📊 Report & Summary"])

# --- TAB 1: ADD & SETTLE ---
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### **📥 Naya Kharcha Add Karein**")
        cat = st.selectbox("Category Chuno:", CATEGORIES)
        amt = st.number_input("Kitne Paise (₹):", min_value=0.0, step=10.0)
        note = st.text_input("Kiske liye? (Note):")
        
        if st.button("💾 CLOUD ME SAVE KAREIN", use_container_width=True):
            if amt > 0:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([now, cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
                st.success(f"✅ ₹{amt} {cat} mein save ho gaye!")
                st.rerun()
            else:
                st.error("Bhai, 0 se zyada amount dalo!")

    with col2:
        st.markdown("### **🤝 Udhar Settle Karein**")
        try:
            all_data = sheet.get_all_records()
            if all_data:
                df_u = pd.DataFrame(all_data)
                if 'Status' in df_u.columns:
                    pending_list = df_u[df_u['Status'] == 'Pending']
                    if not pending_list.empty:
                        st.info(f"Abhi total {len(pending_list)} udhar baaki hain.")
                        selected_u = st.selectbox("Kiska paisa mil gaya?", pending_list['Note'].tolist())
                        
                        if st.button("✅ MARK AS PAID", use_container_width=True):
                            # Sheet mein dhundo aur update karo
                            cell = sheet.find(selected_u)
                            sheet.update_cell(cell.row, 5, "Paid")
                            sheet.update_cell(cell.row, 3, 0) # Balance 0 kar diya
                            st.success(f"Bhai, {selected_u} ka hisab clear!")
                            st.rerun()
                    else:
                        st.write("Sab udhar clear hain! Mast raho. 😎")
        except:
            st.write("Abhi koi pending udhar nahi hai.")

# --- TAB 2: HISTORY & SEARCH ---
with tab2:
    st.markdown("### **🔍 Pura Hisab aur Search**")
    try:
        raw_data = sheet.get_all_records()
        if raw_data:
            df = pd.DataFrame(raw_data)
            
            # Search Box
            search = st.text_input("Kuch bhi likh kar dhundo (Note ya Category):")
            if search:
                df = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)]
            
            # Display Table
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            if st.button("🗑️ Aakhri Entry Delete Karein"):
                sheet.delete_rows(len(sheet.get_all_values()))
                st.warning("Aakhri line sheet se hata di gayi!")
                st.rerun()
        else:
            st.info("Abhi sheet khali hai, pehli entry dalo!")
    except:
        st.error("Data load nahi ho raha.")

# --- TAB 3: REPORTS ---
with tab3:
    st.markdown("### **📊 Kharcha Summary Report**")
    try:
        if raw_data:
            df_rep = pd.DataFrame(raw_data)
            df_rep['Amount'] = pd.to_numeric(df_rep['Amount'])
            
            col_a, col_b = st.columns(2)
            with col_a:
                total = df_rep['Amount'].sum()
                st.metric("KUL KHARCHA", f"₹{total}")
            
            with col_b:
                st.write("**Category ke hisab se kharcha:**")
                st.bar_chart(df_rep.groupby('Category')['Amount'].sum())
                
            st.markdown("---")
            st.write("**📅 Mahine ka Hisab:**")
            df_rep['Month'] = df_rep['Date'].str[:7]
            st.table(df_rep.groupby('Month')['Amount'].sum())
    except:
        st.write("Report dikhane ke liye aur entries chahiye.")

# Sidebar hide/show
st.sidebar.info(f"Logged in: {SHEET_NAME}")
