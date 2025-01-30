import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Function to calculate future value of savings with different interest rates
def future_value(principal, monthly_contribution, years, rate_of_return):
    months = years * 12
    future_values = []
    balance = principal
    for _ in range(months):
        balance += monthly_contribution
        balance *= (1 + rate_of_return / 12)
        future_values.append(balance)
    return future_values

# Interest rates for different account types
account_rates = {
    "High-Interest Savings Account": 0.03,
    "Stock Market Investments": 0.07,
    "Bond Investments": 0.04,
    "Regular Savings Account": 0.01
}

st.title("Future Savings Growth Calculator")

# User inputs
principal = st.number_input("Initial Savings Amount ($):", min_value=0.0, value=1000.0)
monthly_contribution = st.number_input("Monthly Contribution ($):", min_value=0.0, value=200.0)
years = st.number_input("Number of Years to Project:", min_value=1, value=10)

# Account type selection
account_type = st.selectbox("Select Account Type:", list(account_rates.keys()))
rate_of_return = account_rates[account_type]

if st.button("Show Projection"):
    future_values = future_value(principal, monthly_contribution, years, rate_of_return)
    
    # Create a dataframe for visualization
    df = pd.DataFrame({"Month": np.arange(1, years * 12 + 1), "Balance": future_values})
    
    # Display the future savings growth table
    st.write("### Future Savings Growth")
    st.dataframe(df.tail(10))
    
    # Plot the growth
    fig, ax = plt.subplots()
    ax.plot(df["Month"], df["Balance"], label="Projected Savings Growth")
    ax.set_xlabel("Months")
    ax.set_ylabel("Balance ($)")
    ax.set_title("Savings Growth Over Time")
    ax.legend()
    st.pyplot(fig)
