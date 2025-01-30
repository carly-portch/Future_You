import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import itertools

def plot_timeline(timeline_data):
    # Debugging: Print the raw data to check for inconsistencies
    st.write("Debug timeline_data:", timeline_data)
    
    # Check the lengths of all lists
    lengths = {key: len(value) for key, value in timeline_data.items()}
    st.write("Debug lengths:", lengths)
    
    # Find the minimum length of all lists
    min_length = min(lengths.values())
    
    # Trim all lists to the shortest length to ensure consistency
    timeline_data = {key: lst[:min_length] for key, lst in timeline_data.items()}
    
    # Convert to DataFrame
    timeline_df = pd.DataFrame(timeline_data)
    
    # Debugging: Print DataFrame info
    st.write("Debug DataFrame head:", timeline_df.head())
    
    # Plot
    fig, ax = plt.subplots()
    for column in timeline_df.columns:
        ax.plot(timeline_df.index, timeline_df[column], marker='o', label=column)
    
    ax.set_xlabel("Timeline")
    ax.set_ylabel("Values")
    ax.legend()
    st.pyplot(fig)

# Example usage with Streamlit UI
def main():
    st.title("Financial Goals Timeline")
    
    # Example data (replace with real data)
    timeline_data = {
        "Year": [2025, 2030, 2035, 2040],
        "Savings": [10000, 25000, 40000],  # Mismatch in length
        "Investments": [5000, 20000, 35000, 50000]
    }
    
    plot_timeline(timeline_data)
    
if __name__ == "__main__":
    main()
