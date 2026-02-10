import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- GOOGLE SHEETS SETUP ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Apni Sheet ka naam yahan likho (Jo tumne banayi thi)
SHEET_NAME = "Vicku_khata data" 
sheet = client.open(SHEET_NAME).sheet1

# --- CONFIG ---
st.set_page_config(page_title="Vicky's Hub", layout="centered")
CATEGORIES = ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"]

# --- APP UI ---
st.sidebar.title("📱 Vicky's App Store")
selected_app = st.sidebar.selectbox("Kaunsi App Chalani Hai?", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

if selected_app == "🏠 Home":
    st.title("🚀 Welcome Vicky!")
    st.write("Bhai, sidebar se Khata App chuno aur hisab shuru karo.")

elif selected_app == "💰 Khata App":
    st.title("💸 Digital Khata (Google Sheets)")
    
    khata_menu = st.radio("Menu:", ["1. Add", "2. History", "3. Settle Udhar"], horizontal=True)

    if khata_menu == "1. Add":
        st.subheader("➕ Naya Kharcha")
        cat = st.selectbox("Category:", CATEGORIES)
        amount = st.number_input("Amount (₹):", min_value=0.0)
        note = st.text_input("Note:")
        
        if st.button("Save to Google Sheet"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Google Sheet mein data bhejna
            sheet.append_row([now, cat, amount, note, "Pending" if cat=="Udhar" else "N/A"])
            st.success("✅ Google Sheet mein save ho gaya!")

    elif khata_menu == "2. History":
        st.subheader("📜 Pichla Hisab")
        data = sheet.get_all_records()
        if data:
            st.table(data)
        else:
            st.info("Sheet abhi khali hai.")

elif selected_app == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.info("Bhai, Khata set ho gaya hai, ab iska number aayega!")
    
