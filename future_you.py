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

            st.session_state.goals.append({
                'goal_name': goal_name,
                'goal_amount': round(goal_amount),  # Ensure rounding to whole number
                'interest_rate': round(interest_rate),
                'monthly_contribution': round(contribution_amount if contribution_amount else monthly_contribution),  # Ensure rounding to whole number
                'target_year': target_year
            })
            st.success(f"Goal '{goal_name}' added successfully.")
        else:
            st.error("Please enter a valid goal name and amount.")

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

# Sidebar for managing goals
st.sidebar.header("Manage Goals")
if st.session_state.goals:
    for index, goal in enumerate(st.session_state.goals):
        with st.sidebar.expander(goal['goal_name'], expanded=False):
            st.write(f"**Goal Amount:** ${goal['goal_amount']}")
            st.write(f"**Interest Rate:** {goal['interest_rate']}%")
            st.write(f"**Monthly Contribution:** ${goal['monthly_contribution']}")

            # Delete button
            if st.sidebar.button(f"Delete {goal['goal_name']}", key=f"delete_{index}"):
                st.session_state.goals.pop(index)
                st.sidebar.success(f"Goal '{goal['goal_name']}' deleted successfully.")
                st.experimental_rerun()  # Refresh the app

# Monthly contributions section
st.markdown("<h4>Monthly Contributions</h4>", unsafe_allow_html=True)
total_contribution = sum(goal['monthly_contribution'] for goal in st.session_state.goals)
remaining_for_current_you = monthly_income - total_contribution

st.write(f"**Total Monthly Contribution to All Goals:** ${total_contribution}")
st.markdown("### Progress Towards Goals:")
for goal in st.session_state.goals:
    progress = (goal['monthly_contribution'] / goal['goal_amount']) * 100 if goal['goal_amount'] > 0 else 0
    st.progress(int(progress), text=f"{goal['goal_name']}: {int(progress)}%")

st.write(f"**Remaining money to put towards current you:** ${remaining_for_current_you}")

# Snapshot Year Input
st.markdown("---")
st.markdown("<h3 style='color: #FF5722;'>Snapshot</h3>", unsafe_allow_html=True)
snapshot_year = st.number_input("Enter the snapshot year", min_value=current_year, value=current_year)

# Snapshot Button
if st.button("Show Snapshot"):
    # Create snapshot progress bars
    st.markdown("### Progress Towards Goals Snapshot:")
    for goal in st.session_state.goals:
        progress = (goal['monthly_contribution'] / goal['goal_amount']) * 100 if goal['goal_amount'] > 0 else 0
        st.progress(int(progress), text=f"{goal['goal_name']}: {int(progress)}%")

    st.write(f"**Snapshot Year:** {snapshot_year}")
    st.write(f"**Combined Monthly Income:** ${int(round(monthly_income))}")
    st.write(f"**Total Monthly Contribution to All Goals:** ${total_contribution}")
    st.write(f"**Remaining money to put towards current you:** ${remaining_for_current_you}")
