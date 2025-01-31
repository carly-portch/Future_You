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

if "goals" not in st.session_state:
    st.session_state.goals = []

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
    st.session_state.goals.append({
        "Goal Name": goal_name,
        "Goal Amount": goal_amount,
        "Target Date": target_date,
        "Monthly Contribution": monthly_contribution
    })

years = sorted(set(goal["Target Date"].year for goal in st.session_state.goals))
df = {"Year": years, "Amount Saved": np.linspace(0, max(goal["Goal Amount"] for goal in st.session_state.goals), len(years))}
fig = px.line(df, x="Year", y="Amount Saved", title="Goal Timeline")
st.plotly_chart(fig)

st.subheader("Goals List")

goal_to_remove = None
for i, goal in enumerate(st.session_state.goals):
    st.write(f"**Goal Name:** {goal['Goal Name']}")
    st.write(f"**Total Amount Needed:** ${goal['Goal Amount']:.2f}")
    st.write(f"**Target Date:** {goal['Target Date'].strftime('%Y-%m-%d')}")
    st.write(f"**Monthly Contribution:** ${goal['Monthly Contribution']:.2f}")
    
    col1, col2 = st.columns(2)
    if col1.button(f"Edit {goal['Goal Name']}"):
        st.session_state.edit_index = i
    if col2.button(f"Remove {goal['Goal Name']}"):
        goal_to_remove = i  # Mark for deletion
    st.write("---")

# Remove goal after iteration to avoid modifying list during iteration
if goal_to_remove is not None:
    del st.session_state.goals[goal_to_remove]
    st.experimental_rerun()

if "edit_index" in st.session_state:
    index = st.session_state.edit_index
    st.write("## Edit Goal")
    edited_name = st.text_input("Edit Goal Name", value=st.session_state.goals[index]['Goal Name'])
    edited_amount = st.number_input("Edit Goal Amount ($)", min_value=0.01, step=0.01, value=st.session_state.goals[index]['Goal Amount'])
    edited_date = st.date_input("Edit Target Date", value=st.session_state.goals[index]['Target Date'])
    edited_contribution = st.number_input("Edit Monthly Contribution ($)", min_value=0.01, step=0.01, value=st.session_state.goals[index]['Monthly Contribution'])
    
    if st.button("Save Changes"):
        st.session_state.goals[index] = {
            "Goal Name": edited_name,
            "Goal Amount": edited_amount,
            "Target Date": edited_date,
            "Monthly Contribution": edited_contribution
        }
        del st.session_state.edit_index
        st.experimental_rerun()
