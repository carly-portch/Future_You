import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(page_title="Plan Your Future Together", layout="wide")

st.title("Plan Your Future Together")
st.write("""
    This tool helps you and your partner estimate your savings and manage joint medium- and long-term goals.
    Add multiple goals such as a down payment, education, or a dream vacation. You can edit or remove goals after adding them.
    Once you're ready, visualize the timeline below and see how much is left for your 'Current You.'
""")

# Initialize variables
current_year = date.today().year

# Input fields for income
st.subheader("Income")
monthly_income = st.number_input("Enter your combined monthly income after tax", min_value=0.0, value=0.0, key="income_input")

# Initialize goal list
if 'goals' not in st.session_state:
    st.session_state.goals = []

# Function to render a dashed green box with goal info
def render_goal_box(goal_name, goal_amount, monthly_contribution, target_year, index):
    st.markdown(
        f"""
        <div style="border: 2px dashed green; padding: 10px; margin-bottom: 10px; position: relative;">
            <div style="display: flex; justify-content: space-between;">
                <strong>{goal_name}</strong>
                <button style="background-color: red; color: white; border: none; cursor: pointer;" 
                        onclick="document.getElementById('remove-goal-{index}').click()">x</button>
            </div>
            <p><b>Goal Amount:</b> ${goal_amount}</p>
            <p><b>Monthly Contribution:</b> ${monthly_contribution:.2f}</p>
            <p><b>Target Year:</b> {target_year}</p>
            <details>
                <summary style="cursor: pointer;">Edit Goal</summary>
                <div>
                    <input type="text" value="{goal_name}" style="margin-top: 10px;" placeholder="Goal Name">
                    <input type="number" value="{goal_amount}" placeholder="Goal Amount" style="margin-top: 10px;">
                    <input type="number" value="{monthly_contribution}" placeholder="Monthly Contribution" style="margin-top: 10px;">
                    <input type="number" value="{target_year}" placeholder="Target Year" style="margin-top: 10px;">
                </div>
            </details>
        </div>
        """, unsafe_allow_html=True
    )

# Add a goal button expands the form
if st.button("Add another goal"):
    with st.expander("Add a New Goal", expanded=True):
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

        if st.button("Add Goal to Timeline"):
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

# Display each goal in a dashed green box with edit and delete options
st.subheader("Your Goals")
for i, goal in enumerate(st.session_state.goals):
    render_goal_box(goal['goal_name'], goal['goal_amount'], goal['monthly_contribution'], goal['target_year'], i)

    # Add hidden button for removing the goal
    if st.button(f"Remove goal {i}", key=f"remove-goal-{i}"):
        st.session_state.goals.pop(i)
        st.experimental_rerun()

# Plot timeline function (same as before, with timeline adjustments)
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
            f"<b>Current Year:</b> {current_year}<br><b>Combined Monthly Income:</b> ${int(monthly_income)}"
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

    fig.update_layout(title="Joint Life Timeline", xaxis_title="Year", yaxis=dict(visible=False), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Plot the timeline
plot_timeline()
