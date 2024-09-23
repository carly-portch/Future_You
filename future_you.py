import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date
import numpy as np

# Set the title and description of the app
st.title("Plan Your Future Together")
st.write("This tool helps you and your partner estimate your savings and manage joint medium- and long-term goals.")
st.write("Add goals such as a down payment, education, or a dream vacation. Specify the target year or monthly contribution.")

# Initialize current year
current_year = date.today().year

# Input field for combined monthly income
monthly_income = st.number_input("Enter your combined monthly income after tax", min_value=0.0)

# Initialize session state for goals and goal details
if 'goals' not in st.session_state:
    st.session_state.goals = []


def add_goal(goal_name, goal_amount, interest_rate, goal_type, contribution_amount, target_year):
    if goal_name and goal_amount > 0:
        if goal_type == "Monthly Contribution":
            target_year = current_year + int(np.ceil(goal_amount / contribution_amount))
        else:  # Target Year
            months_to_goal = 12 * (target_year - current_year)
            rate_of_return_monthly = interest_rate / 100 / 12
            if rate_of_return_monthly > 0:
                monthly_contribution = goal_amount * rate_of_return_monthly / ((1 + rate_of_return_monthly) ** months_to_goal - 1)
            else:
                monthly_contribution = goal_amount / months_to_goal

        # Append the goal to the session state
        st.session_state.goals.append({
            'goal_name': goal_name,
            'goal_amount': round(goal_amount),
            'monthly_contribution': round(monthly_contribution),
            'target_year': target_year,
            'interest_rate': interest_rate,
            'goal_type': goal_type
        })

        # Add goal to sidebar
        with st.sidebar.expander(goal_name):
            st.write(f"Goal Amount: ${goal_amount}")
            st.write(f"Monthly Contribution: ${monthly_contribution}")

        st.success(f"Goal '{goal_name}' added successfully.")


def plot_timeline():
    if st.session_state.goals:
        latest_year = max(goal['target_year'] for goal in st.session_state.goals)
    else:
        latest_year = current_year

    timeline_data = {
        'Year': [current_year] + [goal['target_year'] for goal in st.session_state.goals],
        'Event': ['Current Year'] + [goal['goal_name'] for goal in st.session_state.goals],
        'Text': [
            f"<b>Current Year:</b> {current_year}<br><b>Combined Monthly Income:</b> ${round(monthly_income)}<br><b>Remaining money to put towards current you:</b> ${round(monthly_income - sum(goal['monthly_contribution'] for goal in st.session_state.goals))}"
        ] + [
            f"<b>Goal:</b> {goal['goal_name']}<br><b>Amount:</b> ${goal['goal_amount']}<br><b>Monthly Contribution:</b> ${goal['monthly_contribution']}"
            for goal in st.session_state.goals
        ]
    }

    # Create the timeline figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[current_year] + [goal['target_year'] for goal in st.session_state.goals],
        y=[0] * (1 + len(st.session_state.goals)),
        mode='markers+text',
        marker=dict(size=12, color='red', line=dict(width=2, color='black')),
        text=['Current Year'] + [goal['goal_name'] for goal in st.session_state.goals],
        textposition='top center',
        hoverinfo='text',
        hovertext=timeline_data['Text']
    ))

    # Add line connecting the markers
    fig.add_trace(go.Scatter(
        x=[current_year
