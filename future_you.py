import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date

st.title("Plan Your Future Together")
st.write("This tool helps you and your partner estimate your savings and manage joint medium- and long-term goals.")
st.write("Add goals such as a down payment, education, or a dream vacation. Specify the target year or monthly contribution. Once set, click 'Add goal to timeline' to include it in the timeline below. Use the panel to remove goals as needed.")

# Initialize variables
current_year = date.today().year

# Input fields for income and expenses
monthly_income = st.number_input("Enter your combined monthly income after tax", min_value=0.0)
monthly_expenses = st.number_input("Enter your combined monthly expenses", min_value=0.0)

# Initialize goal list
if 'goals' not in st.session_state:
    st.session_state.goals = []

# Display goal addition dropdown
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

            # Append goal to session state
            st.session_state.goals.append({
                'goal_name': goal_name,
                'goal_amount': goal_amount,
                'monthly_contribution': contribution_amount if contribution_amount else monthly_contribution,
                'target_year': target_year
            })

            st.success(f"Goal '{goal_name}' added successfully.")
        else:
            st.error("Please enter a valid goal name and amount.")

# Calculate total monthly contribution for current snapshot
def calculate_current_monthly_contribution():
    total_contribution = sum(goal['monthly_contribution'] for goal in st.session_state.goals)
    return total_contribution

# Calculate progress towards each goal for a given snapshot year
def calculate_goal_progress(snapshot_year):
    progress = []
    for goal in st.session_state.goals:
        years_to_snapshot = snapshot_year - current_year
        total_months = 12 * (goal['target_year'] - current_year)
        months_saved = 12 * years_to_snapshot
        amount_saved = min(goal['goal_amount'], (months_saved / total_months) * goal['goal_amount'])
        progress.append((goal['goal_name'], amount_saved, goal['goal_amount']))
    return progress

# Plot timeline
def plot_timeline(snapshot_year=None):
    current_year = date.today().year
    
    # Get latest goal year for timeline end
    if st.session_state.goals:
        latest_year = max(goal['target_year'] for goal in st.session_state.goals)
    else:
        latest_year = current_year

    # Create timeline data
    timeline_data = {
        'Year': [current_year] + [goal['target_year'] for goal in st.session_state.goals],
        'Event': ['Current Year'] + [goal['goal_name'] for goal in st.session_state.goals],
        'Text': [
            f"<b>Current Year:</b> {current_year}<br><b>Combined Monthly Income:</b> ${int(monthly_income)}<br><b>Monthly Expenses:</b> ${int(monthly_expenses)}"
        ] + [
            f"<b>Goal:</b> {goal['goal_name']}<br><b>Amount:</b> ${int(goal['goal_amount'])}<br><b>Monthly Contribution:</b> ${int(goal['monthly_contribution'])}"
            for goal in st.session_state.goals
        ]
    }

    timeline_df = pd.DataFrame(timeline_data)

    # Create the figure
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

    # Add a vertical line for the selected snapshot year if provided
    if snapshot_year is not None:
        fig.add_vline(x=snapshot_year, line_color="blue", line_width=2, annotation_text="Snapshot Year", annotation_position="top right")
    
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

# Show current monthly contribution
current_contribution = calculate_current_monthly_contribution()
st.subheader(f"Current Total Monthly Contribution: ${int(current_contribution)}")

# Allow the user to input a snapshot year and see progress
snapshot_year = st.number_input("Enter a snapshot year to see your progress towards each goal", min_value=current_year, value=current_year)
if st.button("Show Progress"):
    progress_data = calculate_goal_progress(snapshot_year)
    for goal_name, amount_saved, goal_amount in progress_data:
        st.write(f"Goal: {goal_name}")
        st.progress(amount_saved / goal_amount)
        st.write(f"${int(amount_saved)} saved out of ${int(goal_amount)}")

# Plot timeline with the current state
plot_timeline(snapshot_year)
