import streamlit as st

# Initialize the session state if not already present
if 'goals' not in st.session_state:
    st.session_state.goals = []

# Function to add a new goal
def add_goal(goal_name, goal_amount, interest_rate):
    goal = {
        'goal_name': goal_name,
        'goal_amount': goal_amount,
        'interest_rate': interest_rate,
        'editable': False  # Initially set to False
    }
    st.session_state.goals.append(goal)

# Function to toggle edit mode
def toggle_edit(index):
    st.session_state.goals[index]['editable'] = not st.session_state.goals[index]['editable']

# Input fields for new goal
goal_name = st.text_input("Goal Name")
goal_amount = st.number_input("Goal Amount", min_value=0.0)
interest_rate = st.number_input("Rate of Return (%)", min_value=0.0, max_value=100.0)

# Add to Timeline button
if st.button("Add to Timeline"):
    add_goal(goal_name, goal_amount, interest_rate)

# Manage Goals sidebar
with st.sidebar:
    st.header("Manage Goals")
    for index, goal in enumerate(st.session_state.goals):
        st.write(f"**{goal['goal_name']}**")
        st.write(f"Amount: ${goal['goal_amount']}")
        st.write(f"Interest Rate: {goal['interest_rate']}%")

        # Edit and Delete buttons
        if st.button("Edit", key=f"edit_{index}"):
            toggle_edit(index)

        if goal['editable']:
            new_goal_amount = st.number_input("Goal Amount", value=goal['goal_amount'], min_value=0.0, key=f"goal_amount_{index}")
            new_interest_rate = st.number_input("Rate of Return (%)", value=goal['interest_rate'], min_value=0.0, max_value=100.0, key=f"interest_rate_{index}")

            if st.button("Update", key=f"update_{index}"):
                goal['goal_amount'] = new_goal_amount
                goal['interest_rate'] = new_interest_rate
                toggle_edit(index)

        if st.button("Delete", key=f"delete_{index}"):
            st.session_state.goals.pop(index)

# Display the timeline (this can be your original timeline logic)
st.write("Timeline:")
for goal in st.session_state.goals:
    st.write(f"- {goal['goal_name']} for ${goal['goal_amount']} at {goal['interest_rate']}%")
