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

# Function to add new goal
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

        st.success(f"Goal '{goal_name}' added successfully.")

# Function to plot the timeline
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
        x=[current_year] + [goal['target_year'] for goal in st.session_state.goals],
        y=[0] * (1 + len(st.session_state.goals)),
        mode='lines',
        line=dict(color='red', width=2)
    ))

    # Update layout
    fig.update_layout(
        title="Joint Life Timeline",
        xaxis_title='Year',
        yaxis=dict(visible=False),
        xaxis=dict(
            tickmode='array',
            tickvals=[current_year] + [goal['target_year'] for goal in st.session_state.goals],
            ticktext=[f"{current_year}"] + [f"{goal['target_year']}" for goal in st.session_state.goals]
        ),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

# Button to add a new goal
if st.button("Add a New Goal"):
    with st.form("goal_form"):
        st.subheader("Goal Details")
        goal_name = st.text_input("Name of goal", "")
        goal_amount = st.number_input("Goal amount", min_value=0.0)
        interest_rate = st.number_input("Rate of return or interest rate (%)", min_value=0.0, max_value=100.0, value=5.0)
        goal_type = st.radio("Select how you want to calculate your goal", ["Target Year", "Monthly Contribution"], index=0)
        if goal_type == "Monthly Contribution":
            contribution_amount = st.number_input("Monthly contribution towards this goal", min_value=0.0)
            target_year = None
        else:
            contribution_amount = None
            target_year = st.number_input("Target year to reach this goal (yyyy)", min_value=current_year, value=current_year)

        if st.form_submit_button("Add to Timeline"):
            add_goal(goal_name, goal_amount, interest_rate, goal_type, contribution_amount, target_year)

# Sidebar to display existing goals
st.sidebar.header("Existing Goals")
for idx, goal in enumerate(st.session_state.goals):
    with st.sidebar.expander(goal['goal_name'], expanded=True):
        st.write(f"Goal Amount: ${goal['goal_amount']}")
        st.write(f"Monthly Contribution: ${goal['monthly_contribution']}")
        
        # Option to edit
        if st.button(f"Edit Goal {idx}"):
            goal_details = {
                "goal_name": st.text_input("Name of goal", goal['goal_name']),
                "goal_amount": st.number_input("Goal amount", min_value=0.0, value=goal['goal_amount']),
                "interest_rate": st.number_input("Rate of return or interest rate (%)", min_value=0.0, max_value=100.0, value=goal['interest_rate']),
                "goal_type": st.radio("Select how you want to calculate your goal", ["Target Year", "Monthly Contribution"], index=["Target Year", "Monthly Contribution"].index(goal['goal_type'])),
                "contribution_amount": st.number_input("Monthly contribution towards this goal", min_value=0.0) if goal['goal_type'] == "Monthly Contribution" else None,
                "target_year": st.number_input("Target year to reach this goal (yyyy)", min_value=current_year, value=goal['target_year']),
            }
            if st.button("Update Goal"):
                # Update logic here
                st.session_state.goals[idx] = {
                    'goal_name': goal_details['goal_name'],
                    'goal_amount': round(goal_details['goal_amount']),
                    'monthly_contribution': round(goal_details['contribution_amount']) if goal_details['goal_type'] == "Monthly Contribution" else goal['monthly_contribution'],
                    'target_year': goal_details['target_year'],
                    'interest_rate': goal_details['interest_rate'],
                    'goal_type': goal_details['goal_type']
                }
                st.success(f"Goal '{goal_details['goal_name']}' updated successfully.")

        # Option to delete
        if st.button(f"Delete Goal {idx}"):
            st.session_state.goals.pop(idx)
            st.sidebar.success(f"Goal '{goal['goal_name']}' removed successfully.")
            break

# Plot the timeline with the current state
plot_timeline()
