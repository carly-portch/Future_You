import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(layout="wide")  # Full-width layout

st.title("Plan Your Future Together")
st.write("This tool helps you and your partner estimate savings and manage joint goals.")
st.write("Add goals such as a down payment, education, or a dream vacation. You can add multiple goals and manage them easily below.")

# Initialize variables
current_year = date.today().year

# Input columns on the left, output on the right
col1, col2 = st.columns([1, 2])

# Input fields for income (left column)
with col1:
    st.subheader("Input Section")

    monthly_income = st.number_input("Enter your combined monthly income after tax", min_value=0.0)

    st.write("### Add and manage your goals below:")

    if 'goals' not in st.session_state:
        st.session_state.goals = []

    # Display goals in a dashed green box
    with st.container():
        for idx, goal in enumerate(st.session_state.goals):
            with st.expander(f"Goal: {goal['goal_name']}", expanded=True):
                st.write(f"**Goal Amount**: ${goal['goal_amount']}")
                st.write(f"**Monthly Contribution**: ${goal['monthly_contribution']}")
                st.write(f"**Target Year**: {goal['target_year']}")
                # Option to delete the goal
                if st.button(f"Remove Goal '{goal['goal_name']}'", key=f"remove_goal_{idx}"):
                    st.session_state.goals.pop(idx)
                    st.experimental_rerun()  # Trigger a rerun to update the view

    st.write("---")

    # Add goal button expands into form
    with st.expander("Add a New Goal", expanded=True):  # Keep it expanded for editing
        goal_name = st.text_input("Name of goal")
        goal_amount = st.number_input("Goal amount", min_value=0.0)
        interest_rate = st.number_input("Rate of return or interest rate (%)", min_value=0.0, max_value=100.0, value=5.0)
        goal_type = st.radio("Select how you want to calculate your goal", ["Target Year", "Monthly Contribution"])

        contribution_amount = 0
        target_year = current_year  # Default target year for calculation

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
            if target_year > current_year:
                months_to_goal = 12 * (target_year - current_year)
                rate_of_return_monthly = interest_rate / 100 / 12
                if rate_of_return_monthly > 0:
                    contribution_amount = goal_amount * rate_of_return_monthly / ((1 + rate_of_return_monthly) ** months_to_goal - 1)
                else:
                    contribution_amount = goal_amount / months_to_goal

        # Button to add the goal
        if st.button("Add goal to timeline"):
            if goal_name and goal_amount > 0:
                # Store the new goal in session state
                new_goal = {
                    'goal_name': goal_name,
                    'goal_amount': goal_amount,
                    'monthly_contribution': contribution_amount,
                    'target_year': target_year
                }
                st.session_state.goals.append(new_goal)
                st.success(f"Added goal: {goal_name}")  # Feedback for successful addition
                
                # Avoid using experimental rerun immediately to mitigate errors
                st.session_state.goal_name = goal_name
                st.session_state.goal_amount = goal_amount
                st.session_state.interest_rate = interest_rate
                st.session_state.goal_type = goal_type
                st.session_state.contribution_amount = contribution_amount
                st.session_state.target_year = target_year

    # Outputs on the right (col2)
with col2:
    st.subheader("Timeline and Contributions")

    def plot_timeline():
        current_year = date.today().year

        if st.session_state.goals:
            latest_year = max(goal['target_year'] for goal in st.session_state.goals)
        else:
            latest_year = current_year

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

        fig = go.Figure()

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

        fig.add_trace(go.Scatter(
            x=[current_year] + [goal['target_year'] for goal in st.session_state.goals],
            y=[0] * (1 + len(st.session_state.goals)),
            mode='lines',
            line=dict(color='red', width=2)
        ))

        fig.update_layout(
            title="Joint Life Timeline",
            xaxis_title='Year',
            yaxis=dict(visible=False),
            xaxis=dict(tickmode='array', tickvals=[current_year] + [goal['target_year'] for goal in st.session_state.goals],
                       ticktext=[f"{current_year}"] + [f"{goal['target_year']}" for goal in st.session_state.goals]),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # Call plot timeline function
    plot_timeline()

    total_monthly_contribution = sum(goal['monthly_contribution'] for goal in st.session_state.goals)
    remaining_for_current_you = monthly_income - total_monthly_contribution

    st.write(f"**Total Monthly Contribution towards Goals:** ${total_monthly_contribution}")
    st.write(f"**Remaining money to put towards current you:** ${remaining_for_current_you}")

    for goal in st.session_state.goals:
        st.write(f"- {goal['goal_name']}: ${goal['monthly_contribution']} per month")
