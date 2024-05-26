import os
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from deta import Deta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Deta Base setup
DETA_PROJECT_KEY = os.getenv('DETA_PROJECT_KEY')
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base('server_health')

def fetch_data():
    items = []
    res = db.fetch()
    while res.count:
        items.extend(res.items)
        res = db.fetch(last=res.last)
    return items

# Streamlit app
def main():
    st.title('Server Health Dashboard')

    st.write("""
    This dashboard displays the server health data collected over time,
    showing the status code and response time for each check.
    """)

    # Time range selection
    time_range = st.selectbox('Select Time Range', ('Day', 'Week', 'Month'))

    data = fetch_data()

    if data:
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Check if 'timestamp' is present in DataFrame
        if 'timestamp' not in df.columns:
            st.error("Timestamp not found in the data.")
            return

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        # Add color category for heatmap
        df['status'] = df.apply(
            lambda row: 'Green' if row['status_code'] == 200 and row['response_time'] < 3 else 'Red',
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

            # Create heatmap
            plt.figure(figsize=(12, 8))
            heatmap_data = filtered_df.pivot_table(index=filtered_df['timestamp'].dt.date, columns=filtered_df['timestamp'].dt.hour, values='status', aggfunc=lambda x: x)
            sns.heatmap(heatmap_data, cmap={'Green': 'green', 'Red': 'red'}, cbar=False, linewidths=.5, linecolor='black')
            plt.title(f'Server Health Heatmap ({time_range})')
            plt.xlabel('Hour of Day')
            plt.ylabel('Date')

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
