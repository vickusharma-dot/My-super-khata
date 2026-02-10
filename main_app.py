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

# --- APP CONFIG ---
st.set_page_config(page_title="Vicky's Multi-App Hub", layout="centered")

# --- SIDEBAR (HOME / APP SELECTOR) ---
st.sidebar.title("🏠 Main Menu")
app_mode = st.sidebar.radio("App Chuno:", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

# --- HOME SCREEN ---
if app_mode == "🏠 Home":
    st.title("🚀 Vicky's Digital Hub")
    st.write("Bhai, yahan teri saari apps hain. Sidebar se 'Khata App' chuno kaam shuru karne ke liye.")
    st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=100)

# --- KHATA APP (PURANA TERMUX STYLE) ---
elif app_mode == "💰 Khata App":
    st.title("💸 Vicky Khata (Full Options)")
    
    # 1. ADD ENTRY
    st.markdown("### **1. Nayi Entry (Add)**")
    cat = st.selectbox("Category:", ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"])
    amt = st.number_input("Amount (₹):", min_value=0.0)
    note = st.text_input("Note (Kiske liye?):")
    if st.button("💾 SAVE ENTRY"):
        if amt > 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([now, cat, amt, note, "Pending" if cat=="Udhar" else "N/A"])
            st.success("✅ Entry Save Ho Gayi!")
            st.rerun()

    st.divider()

    # 2. SETTLE UDHAR (WITH PARTIAL AMOUNT)
    st.markdown("### **2. Udhar Settle (Hisaab Chukta)**")
    all_rows = sheet.get_all_values()
    if len(all_rows) > 1:
        headers = [h.strip() for h in all_rows[0]]
        df = pd.DataFrame(all_rows[1:], columns=headers)
        pending_udhar = df[df['Status'].str.strip() == 'Pending'].copy()
        
        if not pending_udhar.empty:
            pending_df_display = pending_udhar['Note'] + " (Baaki: ₹" + pending_udhar['Amount'] + ")"
            selected_u = st.selectbox("Kiska udhar kam/khatam karna hai?", pending_df_display.tolist())
            
            settle_amt = st.number_input("Kitne paise mile? (₹):", min_value=0.0)
            
            if st.button("✅ SETTLE KAREIN"):
                # Row dhoondo Date se (Exact match ke liye)
                row_idx = pending_udhar[pending_df_display == selected_u].index[0]
                orig_date = pending_udhar.loc[row_idx, 'Date']
                cell = sheet.find(orig_date)
                
                purana_amt = float(pending_udhar.loc[row_idx, 'Amount'])
                naya_balance = purana_amt - settle_amt
                
                if naya_balance <= 0:
                    sheet.update_cell(cell.row, 5, "Paid") # Status Paid
                    sheet.update_cell(cell.row, 3, 0)      # Amount 0
                    st.success("Bhai, pura hisab clear!")
                else:
                    sheet.update_cell(cell.row, 3, naya_balance) # Sirf balance kam kiya
                    st.warning(f"Bhai, ₹{settle_amt} kam ho gaye. Ab ₹{naya_balance} baaki hain.")
                st.rerun()
        else:
            st.write("Koi udhar pending nahi hai.")

    st.divider()

    # 3. HISTORY & 4. SEARCH
    st.markdown("### **3. Pura Hisab & Khoj (Search)**")
    search_q = st.text_input("🔍 Kuch bhi likh kar search karein:")
    if len(all_rows) > 1:
        hist_df = pd.DataFrame(all_rows[1:], columns=headers)
        if search_q:
            hist_df = hist_df[hist_df.apply(lambda r: search_q.lower() in r.astype(str).str.lower().values, axis=1)]
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

    st.divider()

    # 5. DELETE LAST
    st.markdown("### **5. Galti Sudharein (Delete Last)**")
    if st.button("🗑️ DELETE AAKHRI ENTRY"):
        sheet.delete_rows(len(all_rows))
        st.error("Aakhri line hata di gayi!")
        st.rerun()

    st.divider()

    # 6. REPORTS (SUMMARY)
    st.markdown("### **6. Report & Total**")
    if len(all_rows) > 1:
        rep_df = pd.DataFrame(all_rows[1:], columns=headers)
        rep_df['Amount'] = pd.to_numeric(rep_df['Amount'], errors='coerce').fillna(0)
        st.metric("KUL KHARCHA", f"₹{rep_df['Amount'].sum()}")
        st.bar_chart(rep_df.groupby('Category')['Amount'].sum())

# --- ATM APP (SIDE MEIN) ---
elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.info("Bhai, tune bola tha isko abhi side mein rakhne ka. Jab ready ho bata dena!")

