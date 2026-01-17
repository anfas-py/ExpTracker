import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Quick Spend", layout="centered")

st.title("💸 Quick Expense")

# Connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch data
try:
    df = conn.read(worksheet="Sheet1", usecols=[0, 1, 2])
    df = df.dropna(how="all")
except:
    df = pd.DataFrame(columns=["Date", "Category", "Amount"])

# --- SIMPLE INPUT SECTION ---
# Date and Category in two columns
col_a, col_b = st.columns(2)
with col_a:
    date = st.date_input("Date", datetime.now())
with col_b:
    category = st.selectbox("Category", ["Food", "Travel"])

# Amount input - Pressing 'Enter' here saves the data immediately
amount = st.number_input("Amount", min_value=0.0, step=1.0, key="amount_input")

save_button = st.button("Add Expense", type="primary", use_container_width=True)

# Trigger save if button is clicked OR if amount is entered (and > 0)
if save_button or (amount > 0 and st.session_state.amount_input):
    try:
        new_entry = pd.DataFrame([{
            "Date": date.strftime('%Y-%m-%d'),
            "Category": category,
            "Amount": amount
        }])
        
        # This version clears the cache to ensure we aren't hitting old data errors
        updated_df = pd.concat([df, new_entry], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        
        st.success(f"Saved ₹{amount}!")
        st.balloons()
        st.cache_data.clear() # Clear cache to show new total
        st.rerun()
    except Exception as e:
        st.error(f"Google Sheets is busy or permission is denied. Please check if the 'Bot' is an Editor. Error: {e}")

# --- SUMMARY SECTION ---
st.divider()
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'])
    curr_month = datetime.now().month
    month_df = df[df['Date'].dt.month == curr_month]
    
    # Monthly Total
    total = month_df['Amount'].sum()
    st.subheader(f"Total: ₹{total:,.2f}")
    
    # Visual Breakdown
    food_sum = month_df[month_df['Category'] == 'Food']['Amount'].sum()
    travel_sum = month_df[month_df['Category'] == 'Travel']['Amount'].sum()
    
    st.progress(food_sum / total if total > 0 else 0, text=f"Food: ₹{food_sum}")

    st.progress(travel_sum / total if total > 0 else 0, text=f"Travel: ₹{travel_sum}")
