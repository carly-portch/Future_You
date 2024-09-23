import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date

# Title and Description
st.title("Plan Your Future Together")
st.markdown("""
<div style='background-color: #f9f9f9; padding: 10px; border-radius: 10px;'>
    <h4 style='text-align: center;'>This tool helps you and your partner estimate your savings and manage joint goals. 
    Add multiple goals like a down payment, education, or a vacation.</h4>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Initialize variables
current_year = date.today().year

# Grouping inputs visually
st.markdown("<h3 style='color: #4CAF50;'>Inputs</h3>", unsafe_allow_html=True)

# Input fields for income
monthly_income = st.number_input("Enter your combined monthly income after tax", min_value=0.0)

# Goal Addition
st.markdown("""
<div style='padding: 10px; border: 2px dashed #4CAF50; border-radius: 10px;'>
    <h4>Add a New Goal</h4>
    <p>You can add multiple goals, one at a time.</p>
</div>
""", unsafe_allow_html=True)

if 'goals' not in st.session_state:
    st.session_state.goals = []

# Sidebar for managing goals
st.sidebar.header("Manage Goals")

# Goal input form
with st.expander("Add a Goal"):
    goal_name = st.text_input("Name of goal")
    goal_amount = st.number_input("Goal amount", min_value=0.0)
    interest_rate = st.number_input("Rate of return or interest rate (%)", min_value=0.0, max_value=100.0, value=5.0)
    goal_type = st.radio("Select how you want to calculate your goal", ["Target Year", "Monthly Contribution"])

    if goal_type == "Monthly Contribution":
        contribution_amount = st.number_input("Monthly contribution towards this goal", min_value=0.0)
        if contribution_amount > 0 and goal_amount > 0:
            rate_of_return_monthly = interest_rate / 100 / 12
            if rate_of_return_monthly > 0:
                months_to_goal = np.log(1 + (goal_amount * rate_of_return_monthly) / contribution_amount) / np.log(1 + rate_of_return_monthly)
                target_year = current_year + int(np.ceil(months_to_goal / 12))
            else:
                target_year = current_year + int(goal_amount / contribution_amount // 12)
    elif goal_type == "Target Year":
        target_year = st.number_input("Target year to reach this goal (yyyy)", min_value=current_year)
        contribution_amount = None

    # Add goal button
    if st.button("Add goal to timeline"):
        if goal_name and goal_amount > 0:
            if goal_type == "Monthly Contribution":
                target_year = int(target_year)
            elif goal_type == "Target Year":
                months_to_goal = 12 * (target_year - current_year)
                rate_of_return_monthly = interest_rate / 100 / 12
                if rate_of_return_monthly > 0:
                    monthly_contribution = goal_amount * rate_of_return_monthly / ((1 + rate_of_return_monthly) ** months_to_goal - 1)
                else:
                    monthly_contribution = goal_amount / months_to_goal

            # Add goal to session state
            new_goal = {
                'goal_name': goal_name,
                'goal_amount': round(goal_amount),
                'interest_rate': round(interest_rate),
                'monthly_contribution': round(contribution_amount if contribution_amount else monthly_contribution),
                'target_year': target_year,
                'goal_type': goal_type  # Store goal type for display
            }
            st.session_state.goals.append(new_goal)
            st.success(f"Goal '{goal_name}' added successfully.")
        else:
            st.error("Please enter a valid goal name and amount.")

# Function to display the add goal section
def display_add_goal_section(edit_index=None):
    if edit_index is not None:
        # Pre-fill the values for editing
        goal = st.session_state.goals[edit_index]
        goal_name = goal['goal_name']
        goal_amount = goal['goal_amount']
        interest_rate = goal['interest_rate']
        monthly_contribution = goal['monthly_contribution']
        target_year = goal['target_year']
    else:
        # Default values for a new goal
        goal_name = ""
        goal_amount = 0
        interest_rate = 0.0
        monthly_contribution = 0.0
        target_year = 0

    # Add goal inputs
    goal_name = st.text_input("Name of goal", value=goal_name)
    goal_amount = st.number_input("Goal amount", value=goal_amount, min_value=0)
    interest_rate = st.number_input("Rate of return or interest rate (%)", value=interest_rate, min_value=0.0, max_value=100.0, step=0.1)
    monthly_contribution = st.number_input("Monthly contribution towards this goal", value=monthly_contribution, min_value=0.0)
    target_year = st.number_input("Target Year", value=target_year, min_value=2024)  # Adjust min_value as needed

    # Update/Add Goal button
    if edit_index is not None:
        if st.button("Update", key="update_button"):
            # Update the goal in the session state
            st.session_state.goals[edit_index] = {
                'goal_name': goal_name,
                'goal_amount': goal_amount,
                'interest_rate': interest_rate,
                'monthly_contribution': monthly_contribution,
                'target_year': target_year,
                'goal_type': goal['goal_type']  # Preserve the goal type
            }
            st.success(f"Goal '{goal_name}' updated successfully.")
    else:
        if st.button("Add Goal to Timeline", key="add_goal_button"):
            # Add a new goal to the session state
            st.session_state.goals.append({
                'goal_name': goal_name,
                'goal_amount': goal_amount,
                'interest_rate': interest_rate,
                'monthly_contribution': monthly_contribution,
                'target_year': target_year,
                'goal_type': "Savings"  # Default value, adjust as needed
            })
            st.success(f"Goal '{goal_name}' added successfully.")

# Manage goals section
for index, goal in enumerate(st.session_state.goals):
    with st.sidebar.expander(f"{goal['goal_name']} (Target Year: {goal['target_year']} or Monthly Contribution: {goal['monthly_contribution']})"):
        st.write(f"**Goal Amount:** ${goal['goal_amount']}")
        st.write(f"**Interest Rate:** {goal['interest_rate']}%")
        st.write(f"**Goal Type:** {goal['goal_type']}")

        # Initialize an empty dictionary for editable fields
        editable_fields = {}
        
        # Edit button
        if st.button("Edit Goal", key=f"edit_{index}"):
            editable_fields['goal_name'] = st.text_input("Name of goal", value=goal['goal_name'], key=f"edit_name_{index}")
            editable_fields['goal_amount'] = st.number_input("Goal amount", value=goal['goal_amount'], min_value=0, key=f"edit_amount_{index}")
            editable_fields['interest_rate'] = st.number_input("Rate of return or interest rate (%)", value=goal['interest_rate'], min_value=0.0, max_value=100.0, step=0.1, key=f"edit_rate_{index}")
            editable_fields['monthly_contribution'] = st.number_input("Monthly contribution towards this goal", value=goal['monthly_contribution'], min_value=0.0, key=f"edit_contribution_{index}")

            # Update button
            if st.button("Update Goal", key=f"update_{index}"):
                # Update the goal values in the session state
                st.session_state.goals[index]['goal_name'] = editable_fields['goal_name']
                st.session_state.goals[index]['goal_amount'] = editable_fields['goal_amount']
                st.session_state.goals[index]['interest_rate'] = editable_fields['interest_rate']
                st.session_state.goals[index]['monthly_contribution'] = editable_fields['monthly_contribution']
                st.success(f"Goal '{editable_fields['goal_name']}' updated successfully.")

        # Remove button
        if st.button("Remove Goal", key=f"remove_{index}"):
            st.session_state.goals.pop(index)
            st.success(f"Goal '{goal['goal_name']}' removed successfully.")
            break  # Break to avoid index error after pop


st.markdown("---")
st.markdown("<h3 style='color: #2196F3;'>Outputs</h3>", unsafe_allow_html=True)

# Timeline section
st.markdown("<h4>Joint Life Timeline</h4>", unsafe_allow_html=True)

def plot_timeline(snapshot_year=None):
    # Get latest goal year for timeline end
    latest_year = max(goal['target_year'] for goal in st.session_state.goals) if st.session_state.goals else current_year

    # Create timeline data
    timeline_data = {
        'Year': [current_year] + [goal['target_year'] for goal in st.session_state.goals],
        'Event': ['Current Year'] + [goal['goal_name'] for goal in st.session_state.goals],
        'Text': [
            f"<b>Current Year:</b> {current_year}<br><b>Combined Monthly Income:</b> ${int(round(monthly_income))}"
        ] + [
            f"<b>Goal:</b> {goal['goal_name']}<br><b>Amount:</b> ${int(round(goal['goal_amount']))}<br><b>Monthly Contribution:</b> ${int(round(goal['monthly_contribution']))}"
            for goal in st.session_state.goals
        ]
    }
    timeline_df = pd.DataFrame(timeline_data)

    fig = go.Figure()
    
    # Add red dots for current year and goals
    fig.add_trace(go.Scatter(
        x=[current_year] + [goal['target_year'] for goal in st.session_state.goals], 
        y=[0] * (1 + len(st.session_state.goals)), 
        mode='markers+text', 
        marker=dict(size=12, color='red', line=dict(width=2, color='black')), 
        text=['Current Year'] + [goal['goal_name'] for goal in st.session_state.goals], 
        textposition='top center', 
        hoverinfo='text', 
        hovertext=timeline_df['Text']
    ))
    
    # Add line connecting the red dots
    fig.add_trace(go.Scatter(
        x=[current_year] + [goal['target_year'] for goal in st.session_state.goals], 
        y=[0] * (1 + len(st.session_state.goals)), 
        mode='lines', 
        line=dict(color='red', width=2)
    ))

    fig.update_layout(title="Joint Life Timeline", xaxis_title='Year', yaxis=dict(visible=False), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Show Timeline
plot_timeline()

# Monthly contributions section
st.markdown("<h4>Monthly Contributions</h4>", unsafe_allow_html=True)
total_contribution = sum(goal['monthly_contribution'] for goal in st.session_state.goals)
remaining_for_current_you = monthly_income - total_contribution

st.write(f"**Total Monthly Contribution to All Goals:** ${total_contribution}")
st.markdown("### Breakdown:")
for goal in st.session_state.goals:
    st.write(f"- {goal['goal_name']}: ${int(round(goal['monthly_contribution']))}/month")

st.write(f"**Remaining money to put towards current you:** ${remaining_for_current_you}")
