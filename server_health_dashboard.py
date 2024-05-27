import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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

def create_status_time_series(df, selected_date):
    df = df.copy()  # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df['date'] = df['timestamp'].dt.date
    df['time'] = df['timestamp'].dt.floor('5min')

    selected_df = df[df['date'] == pd.to_datetime(selected_date).date()]

    def determine_status(row):
        if row['status_code'] == 200 and row['response_time'] < 3:
            return 'Green'
        elif row['status_code'] == 200 and row['response_time'] > 3:
            return 'Yellow'
        elif row['status_code'] not in [200, 204]:
            return 'Red'
        else:
            return 'No Data'

    selected_df['status'] = selected_df.apply(determine_status, axis=1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=selected_df['time'],
        y=[1] * len(selected_df),
        marker=dict(color=selected_df['status'].map({
            'Green': 'green',
            'Yellow': 'yellow',
            'Red': 'red',
            'No Data': 'lightgray'
        })),
        width=300000,  # Width of 5 minutes in milliseconds
        hoverinfo='x'
    ))

    fig.update_layout(
        title=f'Uptime Staging Server for {selected_date}',
        xaxis_title='Time',
        yaxis=dict(title='', showticklabels=False),
        showlegend=False
    )

    return fig

def create_response_time_linechart(df, period):
    df = df.copy()  # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df['hour'] = df['timestamp'].dt.floor('h')
    status_map = {'Green': 'green', 'Yellow': 'yellow', 'Red': 'red'}

    df['status'] = df.apply(
        lambda row: 'Green' if row['status_code'] == 200 and row['response_time'] < 3 else 
                    'Yellow' if row['status_code'] == 200 and row['response_time'] > 3 else 'Red',
        axis=1
    )

    fig = go.Figure()

    for status, color in status_map.items():
        status_df = df[df['status'] == status]
        hourly_avg = status_df.groupby('hour')['response_time'].mean().reset_index()
        fig.add_trace(go.Scatter(x=hourly_avg['hour'], y=hourly_avg['response_time'], mode='lines', name=status, line=dict(color=color)))

    fig.update_layout(
        title=f'System Metrics ({period})',
        xaxis_title='Time',
        yaxis_title='Average Response Time (ms)',
        legend_title='Status'
    )

    return fig

# Streamlit app
def main():
    st.title('Server Health Dashboard')

    st.write("""
    This dashboard displays the server health data collected over time,
    showing the uptime and response time for each check.
    """)

    data = fetch_data()

    if data:
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Check if 'timestamp' is present in DataFrame
        if 'timestamp' not in df.columns:
            st.error("Timestamp not found in the data.")
            return

        # Convert timestamps to datetime without timezone conversion
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        # Date filter for time series chart
        st.write("### Uptime Staging Server")
        unique_dates = df['timestamp'].dt.date.unique()
        selected_date = st.date_input('Select Date', value=pd.Timestamp.now().date(), min_value=min(unique_dates), max_value=max(unique_dates))
        filtered_df_date = df[df['timestamp'].dt.date == selected_date]

        if not filtered_df_date.empty:
            fig1 = create_status_time_series(filtered_df_date, selected_date)
            st.plotly_chart(fig1)
        else:
            st.write("No data available for the selected date.")

        # Time range filter for line chart
        st.write("### System Metrics")
        time_range = st.selectbox('Select Time Range', ('Day', 'Week', 'Month'))

        if time_range == 'Day':
            start_time = pd.Timestamp.now() - pd.Timedelta(days=1)
        elif time_range == 'Week':
            start_time = pd.Timestamp.now() - pd.Timedelta(weeks=1)
        elif time_range == 'Month':
            start_time = pd.Timestamp.now() - pd.Timedelta(days=30)

        filtered_df_range = df[df['timestamp'] >= start_time]

        if not filtered_df_range.empty:
            fig2 = create_response_time_linechart(filtered_df_range, time_range)
            st.plotly_chart(fig2)
        else:
            st.write("No data available for the selected time range.")
    else:
        st.write("No data available.")

    # Add a button to manually refresh the data
    if st.button('Refresh'):
        st.rerun()

if __name__ == "__main__":
    main()
