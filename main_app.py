import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Vicky's Pro Khata", layout="centered")

FILE_NAME = "khata_data.json"
BUDGET_FILE = "budget.txt"
CATEGORIES = ["Khana", "Safar", "Petrol", "Party", "Udhar", "Shopping", "Recharge", "Other"]

# --- DATA FUNCTIONS (Termux Logic) ---
def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

def get_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            try: return float(f.read())
            except: return 0
    return 0

# --- UI APP START ---
st.title("💸 Vicky's Pro Khata App")

# SIDEBAR (For ATM & Navigation)
menu = st.sidebar.radio("Main Menu", [
    "1. Kharcha Add Karein", 
    "2. Pura Hisab Dekhein", 
    "3. Udhar Settle Karein", 
    "4. Summary (Category-wise)", 
    "5. Entry Delete Karein",
    "6. Search Karein 🔍",
    "7. Monthly Report 📅",
    "8. Budget Set Karein 💸",
    "🏧 Digital ATM (Under Construction)"
])

data = load_data()

# --- 1. ADD EXPENSE (The 1 to 9 Style) ---
if menu == "1. Kharcha Add Karein":
    st.subheader("➕ Naya Kharcha Likho")
    
    cat = st.selectbox("Category Chuno:", CATEGORIES)
    amount = st.number_input(f"{cat} par kitne paise lage?", min_value=0.0, step=10.0)
    note = st.text_input("Koi note likhna hai? (e.g. Rahul ko diye)")
    
    if st.button("Save Karein"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "date": now,
            "category": cat,
            "amount": amount,
            "original_amount": amount,
            "note": note,
            "status": "Pending" if cat == "Udhar" else "N/A"
        }
        data.append(entry)
        save_data(data)
        st.success(f"✅ {cat} ka kharcha save ho gaya!")
        
        # Budget Alert
        budget = get_budget()
        if budget > 0:
            total_month = sum(e['amount'] for e in data if e['date'][:7] == now[:7])
            if total_month > budget:
                st.warning(f"⚠️ WARNING: Budget hil gaya! Kharcha: ₹{total_month} | Budget: ₹{budget}")

# --- 2. SHOW HISTORY ---
elif menu == "2. Pura Hisab Dekhein":
    st.subheader("📜 Pichla Saara Hisab")
    if data:
        for i, e in enumerate(data):
            st.write(f"{i+1}. **[{e['date']}]** {e['category']}: ₹{e['amount']} - {e['note']} {'['+e.get('status','')+']' if e['category']=='Udhar' else ''}")
    else:
        st.info("Abhi koi data nahi hai.")

# --- 3. SETTLE UDHAR ---
elif menu == "3. Udhar Settle Karein":
    st.subheader("📢 Pending Udhar")
    pending = [e for e in data if e['category'] == "Udhar" and e.get('status') == 'Pending']
    
    if not pending:
        st.success("Chill maro! Koi udhar baki nahi hai.")
    else:
        for p in pending:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"👉 {p['note']} (Baki: ₹{p['amount']})")
            with col2:
                if st.button("Settle", key=p['date']):
                    for d in data:
                        if d['date'] == p['date']:
                            d['status'] = 'Paid'
                            d['amount'] = 0
                    save_data(data)
                    st.rerun()

# --- 4. SUMMARY ---
elif menu == "4. Summary (Category-wise)":
    st.subheader("📊 Category Summary")
    summary = {}
    for e in data:
        summary[e['category']] = summary.get(e['category'], 0) + e['amount']
    
    for c, t in summary.items():
        st.write(f"🔹 {c}: ₹{t}")
    st.divider()
    st.write(f"**💰 Total Kharcha: ₹{sum(summary.values())}**")

# --- 5. DELETE ENTRY ---
elif menu == "5. Entry Delete Karein":
    st.subheader("🗑️ Delete Entry")
    if data:
        entry_list = [f"{i}. {e['date']} - {e['category']} (₹{e['amount']})" for i, e in enumerate(data)]
        to_delete = st.selectbox("Select entry to remove:", entry_list)
        if st.button("Delete"):
            idx = int(to_delete.split('.')[0])
            data.pop(idx)
            save_data(data)
            st.success("Entry deleted!")
            st.rerun()

# --- 6. SEARCH ---
elif menu == "6. Search Karein 🔍":
    query = st.text_input("🔍 Kya dhundna hai?")
    if query:
        results = [e for e in data if query.lower() in e['note'].lower() or query.lower() in e['category'].lower()]
        for r in results:
            st.write(f"✅ {r['date']} | {r['category']} | ₹{r['amount']} | {r['note']}")

# --- 7. MONTHLY REPORT ---
elif menu == "7. Monthly Report 📅":
    st.subheader("📅 Monthly Hisab")
    reports = {}
    for e in data:
        m = e['date'][:7]
        reports[m] = reports.get(m, 0) + e['amount']
    for m, t in reports.items():
        st.write(f"📅 {m} : ₹{t}")

# --- 8. BUDGET SET ---
elif menu == "8. Budget Set Karein 💸":
    curr = get_budget()
    st.write(f"Current Budget: ₹{curr}")
    new_b = st.number_input("Naya Budget dalo:", min_value=0.0)
    if st.button("Set Budget"):
        with open(BUDGET_FILE, "w") as f:
            f.write(str(new_b))
        st.success("Budget set!")

# --- ATM (STILL UNDER CONSTRUCTION) ---
elif menu == "🏧 Digital ATM (Under Construction)":
    st.warning("🚧 Kaam chal raha hai... Agle step mein ise bhi fix karenge!")
    
