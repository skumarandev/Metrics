import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide",
                   
    page_title="Metrics - Dashboard")

with sqlite3.connect('Metrics.db') as conn:
    columns_info = pd.read_sql_query("PRAGMA table_info(Indicators)", conn)
    target_names = ['initiative', 'squad', 'sprint']
    all_columns = columns_info[columns_info['name'].isin(target_names)]['name'].tolist()
    # all_columns = columns_info['name'].tolist()
    # if all_columns:
    #     all_columns.pop(0) # Remove index column

    # 1. Main Layout (80% width)
    spacer_left, main_body, spacer_right = st.columns([1, 8, 1])

    with main_body:
        st.subheader("Indicators Dashboard")

        # 2. Control Dropdown Widths
        # We create 2 narrow columns for the dropdowns inside the 80% area
        col1, col2 = st.columns([2, 2]) # Adjust numbers to change width

        with col1:
            selected_column = st.selectbox("Select a column:", options=all_columns)

        # Fetch values for the chosen column
        unique_vals = pd.read_sql_query(
            f"SELECT DISTINCT \"{selected_column}\" FROM Indicators WHERE \"{selected_column}\" IS NOT NULL", 
            conn
        )[selected_column].tolist()

        with col2:
            selected_values = st.multiselect(f"Select values:", options=unique_vals)

        # 3. Build Query
        query = "SELECT * FROM Indicators"
        if selected_values:
            val_filter = str(tuple(selected_values)).replace(',)', ')')
            query += f" WHERE \"{selected_column}\" IN {val_filter}"



        dfsql = pd.read_sql_query(query, conn)

        def highlight_status(val):

                val_lower = str(val).lower()
                
                if val_lower == 'green':
                    color = 'green'
                elif val_lower == 'amber':
                    color = 'orange'  # Or 'yellow'
                elif val_lower == 'red':
                    color = 'red'
                else:
                    color = ''  # No background for other values
                
                return f'background-color: {color}'

        # Apply it to your DataFrame
        styled_df = dfsql.style.map(highlight_status)

        # 4. Display
        st.dataframe(styled_df, use_container_width=True, height=500, hide_index=True)

       
