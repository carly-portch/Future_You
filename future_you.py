import streamlit as st
import numpy as np
import datetime
import plotly.express as px

def calculate_monthly_contribution(goal_amount, initial_contribution, rate, months):
    """Calculate required monthly contribution given goal amount, initial contribution, rate, and months."""
    if rate == 0:
        return (goal_amount - initial_contribution) / months
    else:
        r = rate / 12  # Convert annual rate to monthly
        return (goal_amount - initial_contribution * (1 + r) ** months) * r / ((1 + r) ** months - 1)

def calculate_months(goal_amount, initial_contribution, rate, monthly_contribution):
    """Calculate required months to achieve the goal given monthly contribution."""
    if rate == 0:
        return np.ceil((goal_amount - initial_contribution) / monthly_contribution)
    else:
        r = rate / 12  # Convert annual rate to monthly
        months = np.log((goal_amount * r / monthly_contribution) + 1) / np.log(1 + r)
        return np.ceil(months)

# Streamlit App UI
st.title("Financial Goal Tracker")

goal_name = st.text_input("Goal Name")
goal_amount = st.number_input("Goal Amount ($)", min_value=0.01, step=0.01)
initial_contribution = st.number_input("Initial Contribution ($)", min_value=0.0, step=0.01)

account_type = st.selectbox("Which account will this money come from?", [
    "Regular Savings Account (0%)",
    "High-Yield Savings Account (2%)",
    "Invested Account (6%)"
])

rates = {
    "Regular Savings Account (0%)": 0.00,
    "High-Yield Savings Account (2%)": 0.02,
    "Invested Account (6%)": 0.06
}
rate = rates[account_type]

option = st.radio("Choose one:", ["Set Target Date", "Set Monthly Contribution"])

if option == "Set Target Date":
    target_date = st.date_input("Target Date", min_value=datetime.date.today())
    months = (target_date.year - datetime.date.today().year) * 12 + (target_date.month - datetime.date.today().month)
    if months > 0:
        monthly_contribution = calculate_monthly_contribution(goal_amount, initial_contribution, rate, months)
        st.write(f"Required Monthly Contribution: **${monthly_contribution:.2f}**")
else:
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.01, step=0.01)
    months = calculate_months(goal_amount, initial_contribution, rate, monthly_contribution)
    target_date = datetime.date.today() + datetime.timedelta(days=int(months * 30))
    st.write(f"Goal Achieved By: **{target_date.strftime('%Y-%m-%d')}**")

if st.button("Add Goal"):
    timeline = [datetime.date.today() + datetime.timedelta(days=i * 30) for i in range(int(months) + 1)]
    values = np.linspace(initial_contribution, goal_amount, len(timeline))
    df = {"Date": timeline, "Amount Saved": values}
    fig = px.line(df, x="Date", y="Amount Saved", title="Goal Timeline")
    st.plotly_chart(fig)
    
    st.subheader("Goal Summary")
    st.write(f"**Goal Name:** {goal_name}")
    st.write(f"**Total Amount Needed:** ${goal_amount:.2f}")
    st.write(f"**Target Date:** {target_date.strftime('%Y-%m-%d')}")
    st.write(f"**Monthly Contribution:** ${monthly_contribution:.2f}")
