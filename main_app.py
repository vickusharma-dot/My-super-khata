import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# --- 1. DATABASE CONNECTION ---
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
except
