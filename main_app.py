import streamlit as st
import json
import os

# --- PAGE SETTINGS ---
st.set_page_config(page_title="Vicky's Hub", page_icon="🚀", layout="centered")

# --- DATA FUNCTIONS (Khata Save/Load karne ke liye) ---
def load_khata():
    if os.path.exists("khata_data.json"):
        with open("khata_data.json", "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_khata(data):
    with open("khata_data.json", "w") as f:
        json.dump(data, f, indent=4)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("📱 Vicky's App Store")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox("Kaunsa App Chalana Hai?", ["🏠 Home", "💰 Super Khata", "🏧 Digital ATM"])

# --- APP 1: HOME ---
if app_mode == "🏠 Home":
    st.title("🚀 Vicky's Digital Hub")
    st.write("Welcome bhai! Ye tumhara apna personal app store hai.")
    st.info("👈 Sidebar ka use karke app badlein.")
    st.image("https://img.icons8.com/clouds/200/000000/smartphone-tablet.png")

# --- APP 2: SUPER KHATA (Working) ---
elif app_mode == "💰 Super Khata":
    st.title("💰 Super Khata")
    
    tab1, tab2 = st.tabs(["➕ Naya Hisab", "📊 Pura Data"])
    
    with tab1:
        with st.form("khata_form", clear_on_submit=True):
            naam = st.text_input("Kiska Naam?")
            item = st.text_input("Kis liye (Reason)?")
            paisa = st.number_input("Amount (₹)", min_value=0)
            submit = st.form_submit_button("Save Karein")
            
            if submit:
                if naam and item:
                    data = load_khata()
                    data.append({"Naam": naam, "Item": item, "Amount": paisa})
                    save_khata(data)
                    st.success(f"✅ {naam} ka hisab save ho gaya!")
                else:
                    st.error("Bhai, naam aur item toh likho!")

    with tab2:
        st.subheader("📋 Sabka Hisab-Kitab")
        data = load_khata()
        if data:
            st.table(data)
            if st.button("Clear All Data"):
                save_khata([])
                st.rerun()
        else:
            st.write("Abhi koi entry nahi hai.")

# --- APP 3: DIGITAL ATM (Under Construction) ---
elif app_mode == "🏧 Digital ATM":
    st.title("🏧 Digital ATM")
    
    st.warning("### 🚧 Work In Progress 🚧")
    st.image("https://img.icons8.com/clouds/200/000000/maintenance.png")
    st.subheader("Bhai, thoda sabr rakho!")
    st.write("Digital ATM ka naya web-version abhi taiyaar ho raha hai. Vicky Bhai is par kaam kar rahe hain.")
    
    # Progress bar for effect
    st.write("Development Progress:")
    st.progress(45)
    st.info("Jaldi hi yahan Deposit aur Withdraw ke buttons aayenge!")
  
