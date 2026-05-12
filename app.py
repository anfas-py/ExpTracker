import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Quick Spend", layout="centered")

st.title("💸 Detailed Expense Tracker")

# Create connection
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CACHED DATA FETCHING ---
@st.cache_data(ttl=600)
def get_data():
    try:
        # Now reading 4 columns to include Remark
        data = conn.read(worksheet="Sheet1", usecols=[0, 1, 2, 3])
        return data.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Remark"])

df = get_data()

# --- INPUT SECTION ---
col_a, col_b = st.columns(2)
with col_a:
    date = st.date_input("Date", datetime.now())
with col_b:
    # Main grouping for easier selection
    main_cat = st.selectbox("Type", ["Food", "Travel", "Other"])

# Sub-category logic
if main_cat == "Food":
    category = st.selectbox("Sub-Category", ["Breakfast", "Lunch", "Dinner", "Snacks/Other"])
elif main_cat == "Travel":
    category = st.selectbox("Sub-Category", ["Car", "Bike", "Bus/Auto/Other"])
else:
    category = "General Other"

amount = st.number_input("Amount", min_value=0.0, step=1.0, key="amount_input")

# New Remark Section
remark = st.text_input("Remark", placeholder="e.g., Canteen, Petrol, Grocery")

save_button = st.button("Add Expense", type="primary", use_container_width=True)

# --- SAVING LOGIC ---
if save_button:
    if amount > 0:
        try:
            new_entry = pd.DataFrame([{
                "Date": date.strftime('%Y-%m-%d'),
                "Category": category,
                "Amount": amount,
                "Remark": remark
            }])
            
            # Fresh read to prevent duplicates
            current_df = conn.read(worksheet="Sheet1", usecols=[0, 1, 2, 3]).dropna(how="all")
            updated_df = pd.concat([current_df, new_entry], ignore_index=True)
            
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.success(f"Saved ₹{amount} for {category}!")
            st.balloons()
            
            st.cache_data.clear()
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter an amount.")

# --- SUMMARY SECTION ---
st.divider()
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'])
    curr_month = datetime.now().month
    month_df = df[df['Date'].dt.month == curr_month]
    
    total = month_df['Amount'].sum()
    st.subheader(f"Monthly Total: ₹{total:,.2f}")
    
    # Optional: Detailed History View
    with st.expander("View Detailed History"):
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
