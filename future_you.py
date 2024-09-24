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
    margin-bottom: 10px;
}

.description {
    background-color: #e6e6fa;  /* Lavender */
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* Section headers */
.section-header {
    color: #1E90FF;  /* Dodger Blue */
    margin: 20px 0 10px 0;
}

/* Input sections */
.input-section {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* Add goal section */
.add-goal-section {
    padding: 15px;
    border: 2px dashed #9370DB;  /* Medium Purple */
    border-radius: 10px;
    margin-bottom: 20px;
    background-color: #f9f9ff;
}

/* Sidebar styles */
.sidebar .sidebar-content {
    padding: 15px;
}

/* Results section */
.results-section {
    border: 2px solid #1E90FF;  /* Dodger Blue */
    padding: 15px;
    border-radius: 10px;
    background-color: #f9f9ff;
    margin-bottom: 20px;
}

/* Timeline */
.plotly-chart {
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Title and Description
st.markdown("<h1 class='title'>The Future You Tool</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='description'>
    <h4>This tool is here to help you visualise your medium and long-term goals. The aim is to help you get clear on what these goals are, their timeline, and how you can make them a reality. This can be used for your family unit, joint goals with a partner, or your own individual financial situation - whatever makes sense for you!
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
st.markdown("<div class='input-section'>", unsafe_allow_html=True)

# Input fields for income
monthly_income = st.number_input(
    "Enter your total monthly income after tax",
    min_value=0.0,
    step=100.0,
    format="%.2f"
)

st.markdown("</div>", unsafe_allow_html=True)

# Add default 'Retirement' goal if not already added and monthly income is provided
if not st.session_state.retirement_goal_added and monthly_income > 0:
    retirement_goal = {
        'goal_name': 'Retirement',
        'goal_amount': int(round(monthly_income * 12 * 25)),
        'current_savings': 0.0,
        'interest_rate': 7.0,
        'monthly_contribution': None,
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
st.markdown("<div class='add-goal-section'>", unsafe_allow_html=True)
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
                months_to_goal = np.log(1 + (goal_amount - current_savings * (1 + rate_of_return_monthly) ** (12 * 100)) / (contribution_amount * rate_of_return_monthly)) / np.log(1 + rate_of_return_monthly)
                target_year = current_year + int(np.ceil(months_to_goal / 12))
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
                    st.error("Invalid calculation due to zero denominator.")
                    st.stop()
                monthly_contribution = (goal_amount - current_savings * (1 + rate_of_return_monthly) ** months_to_goal) * rate_of_return_monthly / denominator
            else:
                monthly_contribution = (goal_amount - current_savings) / months_to_goal
        monthly_contribution = int(round(monthly_contribution))

        # Add goal to session state
        new_goal = {
            'goal_name': goal_name,
            'goal_amount': int(round(goal_amount)),
            'current_savings': float(round(current_savings, 2)),
            'interest_rate': float(interest_rate),
            'monthly_contribution': monthly_contribution,
            'target_year': target_year,
            'goal_type': goal_type
        }
        st.session_state.goals.append(new_goal)
        st.success(f"Added goal: {goal_name}")

        # Reset fields after addition
        goal_name = ""
        goal_amount = 0
        current_savings = 0
        interest_rate = 5.0
        target_year = current_year + 1

st.markdown("</div>", unsafe_allow_html=True)

# Results Section
st.markdown("<h3 class='section-header'>Current Goals</h3>", unsafe_allow_html=True)
st.markdown("<div class='results-section'>", unsafe_allow_html=True)
if st.session_state.goals:
    goals_df = pd.DataFrame(st.session_state.goals)
    st.dataframe(goals_df.style.format({
        'goal_amount': "${:,.0f}",
        'current_savings': "${:,.0f}",
        'monthly_contribution': "${:,.0f}",
        'interest_rate': "{:.1f}%",
    }))
else:
    st.write("No goals added yet.")

# Generate Timeline
st.markdown("<h3 class='section-header'>Timeline</h3>", unsafe_allow_html=True)
timeline_years = [goal['target_year'] for goal in st.session_state.goals if 'target_year' in goal]
timeline_data = [goal['monthly_contribution'] for goal in st.session_state.goals if 'monthly_contribution' in goal]

# Create a timeline chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=timeline_years,
    y=timeline_data,
    mode='markers+lines',
    marker=dict(size=10, color='royalblue'),
    name='Goals Contribution'
))
fig.update_layout(
    title="Goals Timeline",
    xaxis_title="Year",
    yaxis_title="Monthly Contribution ($)",
    xaxis=dict(tickmode='linear', tick0=current_year, dtick=1),
    yaxis=dict(tickprefix="$"),
    showlegend=False
)

# Show timeline chart
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
