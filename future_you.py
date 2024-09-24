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
    color: #333333;
    background-color: #f0f2f6;
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
    color: #4B0082;  /* Indigo */
    margin-top: 30px;
    margin-bottom: 10px;
}

/* Section2 headers */
.section2-header {
    color: black;  /* Black */
    margin-top: 10px;
    margin-bottom: 10px;
}

/* Input sections */
.input-section {
    background-color: #ffffff;
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
    background-color: #f9f9ff;
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
    background-color: #f9f9ff;
    margin-bottom: 30px;
}

/* Timeline */
.plotly-chart {
    margin-bottom: 30px;
}

/* Tooltip styles */
.tooltip {
    display: inline-block;
    position: relative;
    cursor: pointer;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 200px;
    background-color: #555;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 125%; /* Position the tooltip above the text */
    left: 50%;
    margin-left: -100px; /* Center the tooltip */
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}

.info-icon {
    display: inline-block;
    font-size: 14px;
    color: #555;
    margin-left: 5px;
    cursor: pointer;
    vertical-align: middle;
}

.tooltip:hover .info-icon {
    color: #1E90FF;  /* Highlight color on hover */
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)

# Title and Description
st.markdown("<h1 class='title'>The Future You Tool</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='description'>
    <h5>This tool is here to help you visualise your medium and long-term goals. The aim is to help you get clear on what these goals are, their timeline, and how you can make them a reality. This can be used for your family unit, joint goals with a partner, or your own individual financial situation - whatever makes sense for you!
    Add multiple goals like a down payment, education, or a vacation. Play around with different timelines, goal amounts, etc. Have fun and design your dream life! </h5>
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
st.markdown("<h2 class='section-header'>Inputs</h2>", unsafe_allow_html=True)

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
st.markdown("<h3 class='section2-header'>Add a New Goal</h3>", unsafe_allow_html=True)
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

# Rate of return or interest rate input with info icon
st.markdown("""
<div class='tooltip'>Rate of return or interest rate (%)
    <span class='info-icon'>ℹ️</span> 
    <span class='tooltiptext'>This is the expected annual return rate on your investment. It represents the percentage of interest or growth you anticipate on your savings or investments over a year.</span>
</div>
""", unsafe_allow_html=True)

interest_rate = st.number_input(
    "",
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
    if goal_name and goal_amount > 0:
        new_goal = {
            'goal_name': goal_name,
            'goal_amount': int(round(goal_amount)),
            'current_savings': int(round(current_savings)),
            'interest_rate': int(round(interest_rate)),
            'monthly_contribution': int(round(contribution_amount)) if contribution_amount else None,
            'target_year': target_year,
            'goal_type': goal_type
        }
        st.session_state.goals.append(new_goal)
        st.success(f"Goal '{goal_name}' added!")

# Display Goals
st.markdown("<h2 class='section-header'>Your Goals</h2>", unsafe_allow_html=True)
if st.session_state.goals:
    for i, goal in enumerate(st.session_state.goals):
        st.write(f"{goal['goal_name']}: ${goal['goal_amount']} (Current savings: ${goal['current_savings']}, Interest rate: {goal['interest_rate']}%)")
else:
    st.write("No goals added yet.")

# Button to clear all goals
if st.button("Clear All Goals"):
    st.session_state.goals = []
    st.session_state.retirement_goal_added = False
    st.success("All goals have been cleared!")
