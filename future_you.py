import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, datetime

# Set page config for better layout
st.set_page_config(layout="wide")

# Title and Description
st.markdown("<h1 class='title'>The Goal Planning Tool</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='description'>
    <h5>Add multiple goals like a vacation, down payment, education, or a big purchase. You can edit your list of goals in the "Manage Goals" panel on the left.
</div>
""", unsafe_allow_html=True)

# Initialize variables
current_date = date.today()
current_year = current_date.year
current_month = current_date.month

# Initialize session state for goals
if 'goals' not in st.session_state:
    st.session_state.goals = []

# Inputs Section
st.markdown("<h2 class='section-header'>Inputs</h2>", unsafe_allow_html=True)

# Goal Addition
st.markdown("<h4 class='section2-header'>Add a New Goal</h4>", unsafe_allow_html=True)
goal_name = st.text_input("Name of goal")
goal_amount = st.number_input("Goal amount", min_value=0.0, step=100.0, format="%.2f")
current_savings = st.number_input("Initial contribution towards this goal", min_value=0.0, step=100.0, format="%.2f", value=0.0)

account_type = st.radio("Select what type of account you'll use for this goal", ["Regular Savings Account", "High-Yield Savings Account", "Invested Account"])
interest_rates = {"Regular Savings Account": 0.0, "High-Yield Savings Account": 2.0, "Invested Account": 6.0}
interest_rate = interest_rates[account_type]

goal_type = st.radio("Select how you want to calculate your goal", ["Target Date", "Monthly Contribution"])

if goal_type == "Monthly Contribution":
    contribution_amount = st.number_input("Monthly contribution towards this goal", min_value=0.0, step=50.0, format="%.2f")
    if contribution_amount > 0 and goal_amount > 0:
        rate_of_return_monthly = interest_rate / 100 / 12
        months_to_goal = np.log((goal_amount / contribution_amount * rate_of_return_monthly + 1) / ((current_savings * rate_of_return_monthly) + 1)) / np.log(1 + rate_of_return_monthly) if rate_of_return_monthly > 0 else (goal_amount - current_savings) / contribution_amount
        target_date = current_date.replace(month=current_month % 12 + 1, year=current_year + int(np.ceil(months_to_goal / 12)))
else:
    target_year = st.number_input("Target year (yyyy)", min_value=current_year + 1, step=1, format="%d")
    target_month = st.selectbox("Target month", list(range(1, 13)), index=current_month - 1)
    target_date = date(target_year, target_month, 1)
    months_to_goal = (target_date.year - current_year) * 12 + (target_date.month - current_month)
    rate_of_return_monthly = interest_rate / 100 / 12
    monthly_contribution = ((goal_amount - current_savings * (1 + rate_of_return_monthly) ** months_to_goal) * rate_of_return_monthly / ((1 + rate_of_return_monthly) ** months_to_goal - 1)) if rate_of_return_monthly > 0 else (goal_amount - current_savings) / months_to_goal

if st.button("Add goal to timeline"):
    if goal_name and goal_amount > 0 and current_savings >= 0:
        new_goal = {
            'goal_name': goal_name,
            'goal_amount': goal_amount,
            'current_savings': current_savings,
            'interest_rate': interest_rate,
            'monthly_contribution': round(monthly_contribution, 2) if goal_type == "Target Date" else round(contribution_amount, 2),
            'target_date': target_date.strftime("%B %Y"),
            'goal_type': goal_type
        }
        st.session_state.goals.append(new_goal)
        st.success(f"Goal '{goal_name}' added successfully.")
    else:
        st.error("Please enter valid values.")
