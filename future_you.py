import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date

# Set page config for better layout
st.set_page_config(layout="wide")

# Define custom CSS styles
st.markdown("""
<style>
/* General styles */
body {
    font-family: 'Arial', sans-serif;  /* Consistent font */
    color: #333333;  /* Dark Gray */
    background-color: #f0f2f6;  /* Light Gray */
}

/* Title and description */
.title {
    color: #4B0082;  /* Indigo */
    text-align: center;
    margin-bottom: 20px;
}

.description {
    background-color: #e6e6fa;  /* Lavender */
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 30px;
}

/* Section headers */
.section-header {
    color: #1E90FF;  /* Dodger Blue */
    margin-top: 30px;
    margin-bottom: 10px;
    font-size: 1.5em;  /* Larger font size for headers */
}

/* Input sections */
.input-section {
    background-color: #ffffff;  /* White for contrast */
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 30px;
}

/* Add goal section */
.add-goal-section {
    padding: 20px;
    border: 2px dashed #9370DB;  /* Medium Purple */
    border-radius: 10px;
    margin-bottom: 30px;
    background-color: #f9f9ff;  /* Very Light Purple */
}

/* Sidebar styles */
.sidebar .sidebar-content {
    padding: 20px;
}

/* Results section */
.results-section {
    border: 2px solid #1E90FF;  /* Dodger Blue */
    padding: 20px;
    border-radius: 10px;
    background-color: #f9f9ff;  /* Very Light Purple */
    margin-bottom: 30px;
}

/* Timeline */
.plotly-chart {
    margin-bottom: 30px;
}

/* Button styles */
.stButton {
    background-color: #1E90FF;  /* Dodger Blue */
    color: white;  /* White text */
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    cursor: pointer;
}
.stButton:hover {
    background-color: #0B7FFF;  /* Darker blue on hover */
}
</style>
""", unsafe_allow_html=True)

# Title and Description
st.markdown("<h1 class='title'>The Future You Tool</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='description'>
    <h4>This tool is here to help you visualize your medium and long-term goals. The aim is to help you get clear on what these goals are, their timeline, and how you can make them a reality. This can be used for your family unit, joint goals with a partner, or your own individual financial situation - whatever makes sense for you!
    Add multiple goals like a down payment, education, or a vacation. Play around with different timelines, goal amounts, etc. Have fun and design your dream life!</h4>
</div>
""", unsafe_allow_html=True)

# Initialize variables
current_year = date.today().year

# Initialize session state for goals and edit tracking
if 'goals' not in st.session_state:
    st.session_state.goals = []
if 'retirement_goal_added' not in st.session_state:
    st.session_state.retirement_goal_added = False
if 'edit_goal_index' not in st.session_state:
    st.session_state.edit_goal_index = None

# Inputs Section
st.markdown("<h3 class='section-header'>Inputs</h3>", unsafe_allow_html=True)

# Input fields for income
monthly_income = st.number_input(
    "Enter your total monthly income after tax:",
    min_value=0.0,
    step=100.0,
    format="%.2f"
)

# Add default 'Retirement' goal if not already added and monthly income is provided
if not st.session_state.retirement_goal_added and monthly_income > 0:
    retirement_goal = {
        'goal_name': 'Retirement',
        'goal_amount': int(round(monthly_income * 12 * 25)),
        'current_savings': 0.0,  # Initialize with zero savings as float
        'interest_rate': 7.0,
        'monthly_contribution': None,  # Will be calculated below
        'target_year': current_year + 40,
        'goal_type': 'Target Year'
    }
    # Calculate monthly contribution for the retirement goal
    months_to_goal = 12 * (retirement_goal['target_year'] - current_year)
    rate_of_return_monthly = retirement_goal['interest_rate'] / 100 / 12
    if months_to_goal <= 0:
        st.error("Retirement goal target year must be greater than the current year.")
    else:
        if rate_of_return_monthly > 0:
            denominator = (1 + rate_of_return_monthly) ** months_to_goal - 1
            if denominator == 0:
                st.error("Invalid calculation for retirement goal due to zero denominator.")
            else:
                retirement_goal['monthly_contribution'] = (retirement_goal['goal_amount'] - retirement_goal['current_savings'] * (1 + rate_of_return_monthly) ** months_to_goal) * rate_of_return_monthly / denominator
        else:
            retirement_goal['monthly_contribution'] = (retirement_goal['goal_amount'] - retirement_goal['current_savings']) / months_to_goal
        retirement_goal['monthly_contribution'] = int(round(retirement_goal['monthly_contribution']))
        st.session_state.goals.append(retirement_goal)
        st.session_state.retirement_goal_added = True

# Goal Addition
st.markdown("<h3 class='section-header'>Add a New Goal</h3>", unsafe_allow_html=True)
goal_name = st.text_input("Name of goal")
goal_amount = st.number_input(
    "Goal amount",
    min_value=0.0,
    step=100.0,
    format="%.2f"
)
current_savings = st.number_input(
    "Initial contribution towards this goal",
    min_value=0.0,
    step=100.0,
    format="%.2f",
    value=0.0
)
interest_rate = st.number_input(
    "Rate of return or interest rate (%)",
    min_value=0.0,
    max_value=100.0,
    value=5.0,
    step=0.1,
    format="%.1f"
)
goal_type = st.radio("Select how you want to calculate your goal", ["Target Year", "Monthly Contribution"])

if goal_type == "Monthly Contribution":
    contribution_amount = st.number_input(
        "Monthly contribution towards this goal",
        min_value=0.0,
        step=50.0,
        format="%.2f"
    )
    if contribution_amount > 0 and goal_amount > 0:
        rate_of_return_monthly = interest_rate / 100 / 12
        if rate_of_return_monthly > 0:
            try:
                # Adjusted for current_savings
                future_value_contributions = contribution_amount * ((1 + rate_of_return_monthly) ** (12 * 100) - 1) / rate_of_return_monthly
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
    target_year = st.number_input(
        "Target year to reach this goal (yyyy)",
        min_value=current_year + 1,
        step=1,
        format="%d"
    )
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
            if target_year is None or target_year <= current_year:
                st.error("Please enter a valid target year.")
                st.stop()
            months_to_goal = 12 * (int(target_year) - current_year)
            rate_of_return_monthly = interest_rate / 100 / 12
            if months_to_goal <= 0:
                st.error("Target year must be greater than the current year.")
                st.stop()
            if rate_of_return_monthly > 0:
                denominator = (1 + rate_of_return_monthly) ** months_to_goal - 1
                if denominator == 0:
                    st.error("Invalid calculation for target year due to zero denominator.")
                    st.stop()
                monthly_contribution = (goal_amount - current_savings * (1 + rate_of_return_monthly) ** months_to_goal) * rate_of_return_monthly / denominator
            else:
                monthly_contribution = (goal_amount - current_savings) / months_to_goal
            monthly_contribution = int(round(monthly_contribution))
        else:
            st.error("Please select a valid goal type.")
            st.stop()

        new_goal = {
            'goal_name': goal_name,
            'goal_amount': int(round(goal_amount)),
            'current_savings': int(round(current_savings)),
            'interest_rate': interest_rate,
            'monthly_contribution': monthly_contribution,
            'target_year': int(target_year),
            'goal_type': goal_type
        }
        st.session_state.goals.append(new_goal)
        st.success(f"{goal_name} added to goals.")

# Manage Goals
st.markdown("<h3 class='section-header'>Manage Your Goals</h3>", unsafe_allow_html=True)
if st.session_state.goals:
    for idx, goal in enumerate(st.session_state.goals):
        goal_details = f"{goal['goal_name']}: ${goal['goal_amount']} (Current Savings: ${goal['current_savings']}), Monthly Contribution: ${goal['monthly_contribution']}, Target Year: {goal['target_year']}"
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(goal_details)
        with col2:
            if st.button(f"Edit Goal {idx + 1}"):
                st.session_state.edit_goal_index = idx
                goal_name = goal['goal_name']
                goal_amount = goal['goal_amount']
                current_savings = goal['current_savings']
                interest_rate = goal['interest_rate']
                contribution_amount = goal['monthly_contribution']
                goal_type = goal['goal_type']
            if st.button(f"Delete Goal {idx + 1}"):
                st.session_state.goals.pop(idx)
                st.success(f"Goal {goal['goal_name']} deleted.")

# Edit Goal Section
if st.session_state.edit_goal_index is not None:
    st.markdown("<h3 class='section-header'>Edit Selected Goal</h3>", unsafe_allow_html=True)
    editing_goal = st.session_state.goals[st.session_state.edit_goal_index]
    goal_name = st.text_input("Name of goal", editing_goal['goal_name'])
    goal_amount = st.number_input("Goal amount", value=editing_goal['goal_amount'], step=100.0, format="%.2f")
    current_savings = st.number_input("Initial contribution towards this goal", value=editing_goal['current_savings'], step=100.0, format="%.2f")
    interest_rate = st.number_input("Rate of return or interest rate (%)", value=editing_goal['interest_rate'], step=0.1, format="%.1f")
    goal_type = st.radio("Select how you want to calculate your goal", ["Target Year", "Monthly Contribution"], index=0 if editing_goal['goal_type'] == "Target Year" else 1)

    if goal_type == "Monthly Contribution":
        contribution_amount = st.number_input("Monthly contribution towards this goal", value=editing_goal['monthly_contribution'], step=50.0, format="%.2f")
    else:
        target_year = st.number_input("Target year to reach this goal (yyyy)", value=editing_goal['target_year'], min_value=current_year + 1, step=1, format="%d")

    if st.button("Update Goal"):
        updated_goal = {
            'goal_name': goal_name,
            'goal_amount': int(round(goal_amount)),
            'current_savings': int(round(current_savings)),
            'interest_rate': interest_rate,
            'monthly_contribution': contribution_amount,
            'target_year': int(target_year),
            'goal_type': goal_type
        }
        st.session_state.goals[st.session_state.edit_goal_index] = updated_goal
        st.success("Goal updated!")
        st.session_state.edit_goal_index = None  # Reset edit index

# Results Section
st.markdown("<h3 class='section-header'>Your Financial Snapshot</h3>", unsafe_allow_html=True)
if st.session_state.goals:
    total_monthly_contributions = sum(goal['monthly_contribution'] for goal in st.session_state.goals)
    total_goal_amounts = sum(goal['goal_amount'] for goal in st.session_state.goals)
    st.metric(label="Total Monthly Contributions", value=f"${total_monthly_contributions}")
    st.metric(label="Total Goal Amount", value=f"${total_goal_amounts}")

# Timeline
st.markdown("<h3 class='section-header'>Timeline of Goals</h3>", unsafe_allow_html=True)
if st.session_state.goals:
    # Prepare timeline data
    timeline_data = []
    for goal in st.session_state.goals:
        timeline_data.append({
            'Year': goal['target_year'],
            'Goal': goal['goal_name'],
            'Amount': goal['goal_amount'],
            'Contributions': goal['monthly_contribution'],
            'Current Savings': goal['current_savings']
        })

    df_timeline = pd.DataFrame(timeline_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_timeline['Year'],
        y=df_timeline['Amount'],
        mode='markers+lines+text',
        text=df_timeline['Goal'],
        textposition='top center',
        marker=dict(size=10, color='blue'),
        line=dict(width=2, color='blue'),
        name='Goals Timeline'
    ))
    fig.update_layout(title='Timeline of Goals', xaxis_title='Year', yaxis_title='Goal Amount ($)', showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# Show the sidebar with the list of goals
st.sidebar.markdown("<h4>Your Goals</h4>", unsafe_allow_html=True)
for goal in st.session_state.goals:
    st.sidebar.markdown(f"- {goal['goal_name']}: ${goal['goal_amount']} (Current Savings: ${goal['current_savings']})")

