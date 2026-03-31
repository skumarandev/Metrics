import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Scrum Indicators", layout="wide")

# --- DATABASE CONNECTION ---
@st.cache_data # Cache data to improve performance
def get_data():
    conn = sqlite3.connect(r'C:\SampleProjects\Metrics\Metrics.db') 
    # Pulling all relevant columns for both charts
    query = """
    SELECT initiative, squad, sprint, 
           CAST(story_points_completed AS FLOAT) as story_points,
           CAST(team_moral AS FLOAT) as team_moral
    FROM Indicators
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- APP LOGIC ---
st.title("📊 Scrum Metrics Dashboard")

try:
    df = get_data()

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.header("Navigation")
    chart_choice = st.sidebar.selectbox(
        "Choose Analysis View:",
        ["Story Points by Initiative", "Team Morale Heatmap"]
    )

    if chart_choice == "Story Points by Initiative":
        st.subheader("Velocity Analysis")
        # Aggregate data
        df_grouped = df.groupby('initiative')['story_points'].sum().reset_index()

        fig = px.bar(
            df_grouped,
            x='initiative',
            y='story_points',
            title="Total Story Points Completed per Initiative",
            labels={'story_points': 'Total Points', 'initiative': 'Initiative'},
            text_auto=True,
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif chart_choice == "Team Morale Heatmap":
        st.subheader("Team Health Analysis")
        
        # --- HEATMAP FILTER ---
        sprints = ["All"] + sorted(df['sprint'].unique().tolist())
        selected_sprint = st.sidebar.selectbox("Filter by Sprint:", sprints)

        # 1. Create a combined label for the Y-Axis
        df['initiative_squad'] = df['initiative'] + " - " + df['squad']

        # 2. Filter Logic
        plot_df = df.copy()
        if selected_sprint != "All":
            plot_df = plot_df[plot_df['sprint'] == selected_sprint]

        # 3. Pivot using the NEW combined column
        pivot_df = plot_df.pivot_table(
            index='initiative_squad', # Updated index
            columns='sprint', 
            values='team_moral', 
            aggfunc='mean'
        ).sort_index() # Keeps initiatives grouped alphabetically

        # 4. Create the Heatmap
        fig = px.imshow(
            pivot_df,
            labels=dict(x="Sprint", y="Initiative - Squad", color="Morale"),
            x=pivot_df.columns,
            y=pivot_df.index,
            color_continuous_scale='RdYlGn',
            text_auto=True,
            aspect="auto",
            title=f"Team Morale Heatmap ({selected_sprint})",
            template="plotly_dark"
        )
        

        # Adjust layout to ensure Y-axis labels aren't cut off
        fig.update_layout(yaxis={'automargin': True})
        
        st.plotly_chart(fig, use_container_width=True)


    # Raw Data Expander
    with st.expander("View Source Data"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
