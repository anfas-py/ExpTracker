import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Quick Spend", layout="centered")

st.title("💸 Quick Expense")

# Create connection
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CACHED DATA FETCHING ---
# This function only talks to Google once every 10 minutes (600 seconds)
@st.cache_data(ttl=600)
def get_data():
    try:
        data = conn.read(worksheet="Sheet1", usecols=[0, 1, 2])
        return data.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Date", "Category", "Amount"])

df = get_data()

# --- INPUT SECTION ---
col_a, col_b = st.columns(2)
with col_a:
    date = st.date_input("Date", datetime.now())
with col_b:
    category = st.selectbox("Category", ["Food", "Travel"])

amount = st.number_input("Amount", min_value=0.0, step=1.0, key="amount_input")
save_button = st.button("Add Expense", type="primary", use_container_width=True)

# --- SAVING LOGIC ---
if save_button or (amount > 0 and st.session_state.amount_input):
    try:
        new_entry = pd.DataFrame([{
            "Date": date.strftime('%Y-%m-%d'),
            "Category": category,
            "Amount": amount
        }])
        
        # Combine current data with new entry
        updated_df = pd.concat([df, new_entry], ignore_index=True)
        
        # Write back to Google
        conn.update(worksheet="Sheet1", data=updated_df)
        
        st.success(f"Saved ₹{amount}!")
        
        # IMPORTANT: Clear the cache so the NEXT run fetches the new total
        st.cache_data.clear()
        st.rerun()
        
    except Exception as e:
        if "429" in str(e):
            st.error("Google is tired! Wait 60 seconds and try again. (Quota Limit)")
        else:
            st.error(f"Error: {e}")

# --- SUMMARY SECTION ---
st.divider()
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'])
    curr_month = datetime.now().month
    month_df = df[df['Date'].dt.month == curr_month]
    
    total = month_df['Amount'].sum()
    st.subheader(f"Total: ₹{total:,.2f}")
    
    food_sum = month_df[month_df['Category'] == 'Food']['Amount'].sum()
    travel_sum = month_df[month_df['Category'] == 'Travel']['Amount'].sum()
    
    st.progress(food_sum / total if total > 0 else 0, text=f"Food: ₹{food_sum}")
    st.progress(travel_sum / total if total > 0 else 0, text=f"Travel: ₹{travel_sum}")
