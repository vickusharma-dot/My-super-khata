import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Vicky's App Store", layout="centered")

# --- DATA LOGIC (Termux wali files) ---
FILE_NAME = "khata_data.json"
BUDGET_FILE = "budget.txt"
CATEGORIES = ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"]

def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

# --- SIDEBAR: APP SELECTION ---
st.sidebar.title("📱 Vicky's App Store")
st.sidebar.markdown("---")
selected_app = st.sidebar.selectbox("Kaunsi App Chalani Hai?", ["🏠 Home", "💰 Khata App", "🏧 Digital ATM"])

# --- APP 1: HOME ---
if selected_app == "🏠 Home":
    st.title("🚀 Welcome to Vicky's Hub")
    st.write("Bhai, sidebar se app select karo aur kaam shuru karo!")
    st.image("https://img.icons8.com/clouds/200/000000/smartphone-tablet.png")

# --- APP 2: KHATA APP (Pure Options ke saath) ---
elif selected_app == "💰 Khata App":
    st.title("💸 Digital Khata")
    
    # APP KE ANDAR KA MENU (Yahan wahi 1-9 options hain)
    khata_menu = st.radio("Khata Menu:", [
        "1. Kharcha Add Karein", 
        "2. Pura Hisab Dekhein", 
        "3. Udhar Settle Karein", 
        "4. Summary (Category-wise)", 
        "5. Entry Delete Karein",
        "6. Search Karein 🔍",
        "7. Monthly Report 📅",
        "8. Budget Set Karein 💸"
    ], horizontal=True) # Horizontal se buttons jaise dikhenge
    
    st.markdown("---")
    data = load_data()

    if khata_menu == "1. Kharcha Add Karein":
        st.subheader("➕ Naya Kharcha")
        cat = st.selectbox("Category:", CATEGORIES)
        amount = st.number_input(f"{cat} Amount (₹):", min_value=0.0)
        note = st.text_input("Note (Kiske liye?):")
        if st.button("Save Karein"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data.append({"date": now, "category": cat, "amount": amount, "note": note, "status": "Pending" if cat=="Udhar" else "N/A"})
            save_data(data)
            st.success("Save ho gaya!")

    elif khata_menu == "2. Pura Hisab Dekhein":
        st.subheader("📜 Pichla Hisab")
        if data: st.table(data)
        else: st.info("Khali hai bhai!")

    elif khata_menu == "3. Udhar Settle Karein":
        st.subheader("📢 Pending Udhar")
        for i, e in enumerate(data):
            if e['category'] == "Udhar" and e.get('status') == 'Pending':
                col1, col2 = st.columns([3, 1])
                col1.write(f"{e['note']} - ₹{e['amount']}")
                if col2.button("Settle", key=f"btn_{i}"):
                    data[i]['status'] = 'Paid'
                    save_data(data)
                    st.rerun()

    elif khata_menu == "4. Summary (Category-wise)":
        st.subheader("📊 Totals")
        summary = {}
        for e in data: summary[e['category']] = summary.get(e['category'], 0) + e['amount']
        st.write(summary)

    # ... Baki options (Search, Delete, Report) bhi isi tarah niche chalte rahenge ...
    else:
        st.write(f"{khata_menu} par kaam chal raha hai, par logic vahi hai!")

# --- APP 3: DIGITAL ATM ---
elif selected_app == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    st.warning("### 🚧 UNDER CONSTRUCTION 🚧")
    st.image("https://img.icons8.com/clouds/200/000000/maintenance.png")
    st.write("Vicky bhai, is app par abhi kaam chal raha hai. Jaldi hi PIN system wala ATM yahan dikhega!")
    
