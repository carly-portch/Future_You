import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date

# Set page config for better layout
st.set_page_config(layout="wide")

# Title
st.title("The Future You Tool")

# Initialize session state for goals
if 'goals' not in st.session_state:
    st.session_state.goals = []

current_year = date.today().year

# Input fields for income
monthly_income = st.number_input("Enter your total monthly income after tax:", min_value=0.0, step=100.0, format="%.2f")

# Goal Addition
st.header("Add a New Goal")
goal_name = st.text_input("Name of goal")
goal_amount = st.number_input("Goal amount", min_value=0.0, step=100.0, format="%.2f")
current_savings = st.number_input("Initial contribution towards this goal", min_value=0.0, step=100.0, format="%.2f", value=0.0)

# Replace rate of return input with account selection
account_type = st.radio("What account would the money be taken from?", 
                        ["Regular savings account", "High yield savings account", "Investing account"])

# Assign interest rate based on account type
interest_rates = {"Regular savings account": 0.0, "High yield savings account": 2.0, "Investing account": 6.0}
interest_rate = interest_rates[account_type]

goal_type = st.radio("Select how you want to calculate your goal", ["Target Year", "Monthly Contribution"])

if goal_type == "Monthly Contribution":
    contribution_amount = st.number_input("Monthly contribution towards this goal", min_value=0.0, step=50.0, format="%.2f")
    if contribution_amount > 0 and goal_amount > 0:
        rate_of_return_monthly = interest_rate / 100 / 12
        if rate_of_return_monthly > 0:
            try:
                target_year = current_year + int(np.ceil(np.log((goal_amount - current_savings * (1 + rate_of_return_monthly) ** (12 * 100)) / (contribution_amount * rate_of_return_monthly) + 1) / np.log(1 + rate_of_return_monthly)))
            except:
                st.error("Invalid calculation for months to goal.")
                target_year = current_year + 1
        else:
            try:
                months_to_goal = (goal_amount - current_savings) / contribution_amount
                target_year = current_year + int(np.ceil(months_to_goal / 12))
            except:
                target_year = current_year + 1
elif goal_type == "Target Year":
    target_year = st.number_input("Target year to reach this goal (yyyy)", min_value=current_year + 1, step=1, format="%d")
    contribution_amount = None

# Add goal button
if st.button("Add goal to timeline"):
    if goal_name and goal_amount > 0 and current_savings >= 0:
        if goal_type == "Monthly Contribution":
            if contribution_amount is None or contribution_amount <= 0:
                st.error("Please enter a valid monthly contribution amount.")
                st.stop()
            target_year = int(target_year)
            monthly_contribution = contribution_amount
        elif goal_type == "Target Year":
            months_to_goal = 12 * (int(target_year) - current_year)
            rate_of_return_monthly = interest_rate / 100 / 12
            if months_to_goal <= 0:
                st.error("Target year must be greater than the current year.")
                st.stop()
            if rate_of_return_monthly > 0:
                denominator = (1 + rate_of_return_monthly) ** months_to_goal - 1
                if denominator == 0:
                    st.error("Invalid calculation due to zero denominator.")
                    st.stop()
                monthly_contribution = (goal_amount - current_savings * (1 + rate_of_return_monthly) ** months_to_goal) * rate_of_return_monthly / denominator
            else:
                monthly_contribution = (goal_amount - current_savings) / months_to_goal
        monthly_contribution = int(round(monthly_contribution))
        
        new_goal = {
            'goal_name': goal_name,
            'goal_amount': int(round(goal_amount)),
            'current_savings': float(round(current_savings, 2)),
            'interest_rate': round(interest_rate, 2),
            'monthly_contribution': monthly_contribution,
            'target_year': int(target_year),
            'goal_type': goal_type
        }
        st.session_state.goals.append(new_goal)
        st.success(f"Goal '{goal_name}' added successfully.")
