import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import calmap
from deta import Deta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Deta Base setup
DETA_PROJECT_KEY = os.getenv('DETA_PROJECT_KEY')
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base('server_health')

def fetch_data():
    res = db.fetch()
    all_items = res.items
    while res.last:
        res = db.fetch(last=res.last)
        all_items += res.items
    return all_items

# Streamlit app
def main():
    st.title('Server Health Dashboard')

    st.write("""
    This dashboard displays the server health data collected over time,
    showing the status code and response time for each check.
    """)

    data = fetch_data()

    st.write(data)

    # Time range selection
    time_range = st.selectbox('Select Time Range', ('Day', 'Week', 'Month'))

    if data:
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Check if 'timestamp' is present in DataFrame
        if 'timestamp' not in df.columns:
            st.error("Timestamp not found in the data.")
            return

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        # Add numeric status category for heatmap
        df['status_numeric'] = df.apply(
            lambda row: 1 if row['status_code'] == 200 and row['response_time'] < 3 else 0,
            axis=1
        )

        if time_range == 'Day':
            start_time = pd.Timestamp.now() - pd.Timedelta(days=1)
        elif time_range == 'Week':
            start_time = pd.Timestamp.now() - pd.Timedelta(weeks=1)
        elif time_range == 'Month':
            start_time = pd.Timestamp.now() - pd.Timedelta(days=30)

        # Filter data based on the selected time range
        filtered_df = df[df['timestamp'] >= start_time]

        if not filtered_df.empty:
            st.write(f"## Status Code and Response Time Heatmap ({time_range})")

            # Create a Series for calmap
            calmap_data = filtered_df.set_index('timestamp')['status_numeric']

            plt.figure(figsize=(12, 8))
            calmap.calendarplot(calmap_data, cmap='RdYlGn', fillcolor='grey', linewidth=0.5)
            plt.title(f'Server Health Heatmap ({time_range})')

            st.pyplot(plt)
        else:
            st.write("No data available for the selected time range.")
    else:
        st.write("No data available.")

    # Add a button to manually refresh the data
    if st.button('Refresh'):
        st.rerun()

if __name__ == "__main__":
    main()
