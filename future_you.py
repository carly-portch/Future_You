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
    color: #1E90FF;  /* Dodger Blue */
    margin-top: 30px;
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
</style>
""", unsafe_allow_html=True)

# Title and Description
st.markdown("<h1 class='title'>The Future You Tool</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='description'>
    <h4>This tool is here to help you visualise your medium and long-term goals. The aim is to help you get clear on what these goals are, their timeline, and how you can make them a reality. This can be used for your family unit, joint goals with a partner, or your own individual financial situation - whatever makes sense for you!
    Add multiple goals like a down payment, education, or a vacation. Play around with different timelines, goal amounts, etc. Have fun and design your dream life! </h4>
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
                    st.error("Invalid calculation due to zero denominator.")
                    st.stop()
                monthly_contribution = (goal_amount - current_savings * (1 + rate_of_return_monthly) ** months_to_goal) * rate_of_return_monthly / denominator
            else:
                monthly_contribution = (goal_amount - current_savings) / months_to_goal
        monthly_contribution = int(round(monthly_contribution))

        # Add goal to session state
        new_goal = {
            'goal_name': goal_name,
            'goal_amount': int(round(goal_amount)),  # Ensure integer
            'current_savings': float(round(current_savings, 2)),
            'interest_rate': round(interest_rate, 2),
            'monthly_contribution': monthly_contribution,  # Ensure integer
            'target_year': int(target_year),
            'goal_type': goal_type  # Store goal type for display
        }
        st.session_state.goals.append(new_goal)
        st.success(f"Goal '{goal_name}' added successfully.")
    else:
        st.error("Please enter a valid goal name, amount, and Initial contribution.")
st.markdown("</div>", unsafe_allow_html=True)

# Sidebar for managing goals
st.sidebar.header("Manage Goals")

# Manage goals section
for index, goal in enumerate(st.session_state.goals):
    with st.sidebar.expander(f"{goal['goal_name']} (Target Year: {goal['target_year']}, Monthly Contribution: ${goal['monthly_contribution']})"):
        st.write(f"**Goal Amount:** ${goal['goal_amount']}")
        st.write(f"**Initial contribution:** ${int(round(goal['current_savings']))}")
        st.write(f"**Interest Rate:** {goal['interest_rate']}%")
        st.write(f"**Goal Type:** {goal['goal_type']}")
        
        # Check if this goal is being edited
        if st.session_state.edit_goal_index == index:
            # Editable fields
            edited_goal_name = st.text_input(
                "Name of goal",
                value=goal['goal_name'],
                key=f"edit_name_{index}"
            )
            
            edited_goal_amount = st.number_input(
                "Goal amount",
                value=goal['goal_amount'],
                min_value=0,
                step=1,
                format="%d",
                key=f"edit_amount_{index}"
            )
            
            edited_current_savings = st.number_input(
                "Initial contribution towards this goal",
                value=goal['current_savings'],
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key=f"edit_current_savings_{index}"
            )
            
            edited_interest_rate = st.number_input(
                "Rate of return or interest rate (%)",
                value=goal['interest_rate'],
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
                key=f"edit_rate_{index}"
            )
            
            edited_goal_type = st.radio(
                "Select how you want to calculate your goal",
                ["Target Year", "Monthly Contribution"],
                index=0 if goal['goal_type'] == "Target Year" else 1,
                key=f"edit_goal_type_{index}"
            )
            
            if edited_goal_type == "Monthly Contribution":
                edited_contribution_amount = st.number_input(
                    "Monthly contribution towards this goal",
                    value=float(goal['monthly_contribution']),
                    min_value=0.0,
                    step=50.0,
                    format="%.2f",
                    key=f"edit_contribution_{index}"
                )
                # Recalculate target_year based on new contribution
                if edited_contribution_amount > 0 and edited_goal_amount > 0:
                    rate_of_return_monthly = edited_interest_rate / 100 / 12
                    if rate_of_return_monthly > 0:
                        try:
                            # Adjusted for current_savings
                            # Using future value formula to estimate months_to_goal
                            months_to_goal = np.log(1 + (edited_goal_amount - edited_current_savings * (1 + rate_of_return_monthly) ** (12 * 100)) / (edited_contribution_amount * rate_of_return_monthly)) / np.log(1 + rate_of_return_monthly)
                            target_year_calculated = current_year + int(np.ceil(months_to_goal / 12))
                        except:
                            st.error("Invalid calculation for months to goal.")
                            target_year_calculated = current_year + 1
                    else:
                        try:
                            months_to_goal = (edited_goal_amount - edited_current_savings) / edited_contribution_amount
                            target_year_calculated = current_year + int(np.ceil(months_to_goal / 12))
                        except:
                            target_year_calculated = current_year + 1
            elif edited_goal_type == "Target Year":
                edited_target_year = st.number_input(
                    "Target Year",
                    value=goal['target_year'],
                    min_value=current_year + 1,
                    step=1,
                    format="%d",
                    key=f"edit_target_year_{index}"
                )
            
            # Update button
            if st.button("Update Goal", key=f"update_{index}"):
                if edited_goal_type == "Target Year":
                    months_to_goal = 12 * (int(edited_target_year) - current_year)
                    rate_of_return_monthly = edited_interest_rate / 100 / 12
                    if months_to_goal <= 0:
                        st.error("Target year must be greater than the current year.")
                        st.stop()
                    if rate_of_return_monthly > 0:
                        denominator = (1 + rate_of_return_monthly) ** months_to_goal - 1
                        if denominator == 0:
                            st.error("Invalid calculation due to zero denominator.")
                            st.stop()
                        edited_monthly_contribution = (edited_goal_amount - edited_current_savings * (1 + rate_of_return_monthly) ** months_to_goal) * rate_of_return_monthly / denominator
                    else:
                        edited_monthly_contribution = (edited_goal_amount - edited_current_savings) / months_to_goal
                else:
                    # For "Monthly Contribution", recalculate target_year
                    contribution_amount = edited_contribution_amount
                    rate_of_return_monthly = edited_interest_rate / 100 / 12
                    if contribution_amount <= 0:
                        st.error("Monthly contribution must be greater than zero.")
                        st.stop()
                    if rate_of_return_monthly > 0:
                        try:
                            # Adjusted for current_savings
                            months_to_goal = np.log(1 + (edited_goal_amount - edited_current_savings * (1 + rate_of_return_monthly) ** months_to_goal) / (contribution_amount * rate_of_return_monthly)) / np.log(1 + rate_of_return_monthly)
                            edited_target_year = current_year + int(np.ceil(months_to_goal / 12))
                        except:
                            st.error("Invalid calculation for months to goal.")
                            edited_target_year = current_year + 1
                    else:
                        try:
                            months_to_goal = (edited_goal_amount - edited_current_savings) / contribution_amount
                            edited_target_year = current_year + int(np.ceil(months_to_goal / 12))
                        except:
                            edited_target_year = current_year + 1
                    edited_monthly_contribution = int(round(contribution_amount))
                
                # Ensure monthly_contribution is integer after recalculation
                edited_monthly_contribution = int(round(edited_monthly_contribution)) if edited_goal_type == "Target Year" else int(round(edited_monthly_contribution))
                
                # Update the goal values in the session state
                st.session_state.goals[index] = {
                    'goal_name': edited_goal_name,
                    'goal_amount': int(edited_goal_amount),
                    'current_savings': float(round(edited_current_savings, 2)),
                    'interest_rate': round(edited_interest_rate, 2),
                    'monthly_contribution': edited_monthly_contribution,
                    'target_year': int(edited_target_year),
                    'goal_type': edited_goal_type
                }
                st.success(f"Goal '{edited_goal_name}' updated successfully.")
                # Reset edit_goal_index
                st.session_state.edit_goal_index = None
            
            # Cancel Edit button
            if st.button("Cancel", key=f"cancel_{index}"):
                st.session_state.edit_goal_index = None

        else:
            # Edit button
            if st.button("Edit Goal", key=f"edit_{index}"):
                st.session_state.edit_goal_index = index

            # Remove button
            if st.button("Remove Goal", key=f"remove_{index}"):
                st.session_state.goals.pop(index)
                st.success(f"Goal '{goal['goal_name']}' removed successfully.")
                # If the removed goal was being edited, reset edit_goal_index
                if st.session_state.edit_goal_index == index:
                    st.session_state.edit_goal_index = None
                # Adjust edit_goal_index if necessary
                elif st.session_state.edit_goal_index is not None and st.session_state.edit_goal_index > index:
                    st.session_state.edit_goal_index -= 1
                break  # Exit after removal to prevent index issues

# Outputs Section
st.markdown("<h3 class='section-header'>Outputs</h3>", unsafe_allow_html=True)

# Timeline section
st.markdown("<h4>My Timeline</h4>", unsafe_allow_html=True)

def plot_timeline():
    # Get latest goal year for timeline end
    if st.session_state.goals:
        latest_year = max(goal['target_year'] for goal in st.session_state.goals)
    else:
        latest_year = current_year

    # Create timeline data
    total_contribution = sum(goal['monthly_contribution'] for goal in st.session_state.goals)
    remaining_for_current_you = monthly_income - total_contribution
    timeline_data = {
        'Year': [current_year] + [goal['target_year'] for goal in st.session_state.goals],
        'Event': ['Current Year'] + [goal['goal_name'] for goal in st.session_state.goals],
        'Text': [
            f"<b>Year:</b> {current_year}<br><b>Monthly Income:</b> ${int(round(monthly_income))}<br><b>Monthly contributions towards goals:</b> ${int(round(total_contribution))}<br><b>Monthly money remaining for current you:</b> ${int(round(remaining_for_current_you))}"
        ] + [
            f"<b>Year:</b> {goal['target_year']}<br><b>Goal Name:</b> {goal['goal_name']}<br><b>Goal Amount:</b> ${int(round(goal['goal_amount']))}<br><b>Initial Contribution:</b> ${int(round(goal['current_savings']))}<br><b>Monthly Contribution:</b> ${int(round(goal['monthly_contribution']))}"
            for goal in st.session_state.goals
        ]
    }
    timeline_df = pd.DataFrame(timeline_data)

    fig = go.Figure()

    # Add purple dots for current year and goals
    fig.add_trace(go.Scatter(
        x=timeline_df['Year'],
        y=[0] * len(timeline_df),
        mode='markers+text',
        marker=dict(size=12, color='#800080', line=dict(width=2, color='black')),  # Purple
        text=timeline_df['Event'],
        textposition='top center',
        hoverinfo='text',
        hovertext=timeline_df['Text']
    ))

    # Add line connecting the dots
    fig.add_trace(go.Scatter(
        x=timeline_df['Year'],
        y=[0] * len(timeline_df),
        mode='lines',
        line=dict(color='black', width=2)
    ))

    fig.update_layout(xaxis_title='Year', yaxis=dict(visible=False), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Show Timeline
plot_timeline()

# Monthly Contribution Results Section
# Check if goals exist in session state
if 'goals' in st.session_state and st.session_state.goals:
    total_contribution = sum(goal['monthly_contribution'] for goal in st.session_state.goals)
    remaining_for_current_you = monthly_income - total_contribution

    # Add a thick horizontal line before the results section
    st.markdown("<hr style='height: 4px; background-color: black;'>", unsafe_allow_html=True)

    # Display the Monthly Breakdown header
    st.markdown("<h2>Monthly Breakdown</h2>", unsafe_allow_html=True)

    # Display the total contribution to goals
    st.markdown(f"""
        <h3 style='color: #1E90FF;'>Monthly Contributions Towards Goals:</h3>
        <h4 style='color: #1E90FF;'>Total Monthly Contribution to All Goals: <b>${int(round(total_contribution))}</b></h4>
        <ul>
    """, unsafe_allow_html=True)

    # Loop through the goals and include them directly under the total contributions number
    for goal in st.session_state.goals:
        st.markdown(f"<li><b>{goal['goal_name']}:</b> ${int(round(goal['monthly_contribution']))}/month</li>", unsafe_allow_html=True)

    # Close the unordered list and display the remaining money section
    st.markdown(f"""
        </ul>
        <h3 style='color: #1E90FF;'>Remaining money to put towards current you:</h3>
        <div style='border: 2px solid red; background-color: rgba(255, 0, 0, 0.2); padding: 10px; border-radius: 5px;'>
            <b>${int(round(remaining_for_current_you))}</b>
        </div>
    """, unsafe_allow_html=True)

else:
    # Add a thick horizontal line for no goals message
    st.markdown("<hr style='height: 4px; background-color: black;'>", unsafe_allow_html=True)
    st.markdown("<h3>No goals have been added yet.</h3>", unsafe_allow_html=True)
