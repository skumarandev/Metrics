import streamlit as st
import pandas as pd
import sqlite3

# Title of the app
st.title("Upload the metrics file")

# 1. Create the file uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

if uploaded_file is not None:
    # 2. Read the CSV into a pandas DataFrame
    df = pd.read_csv(uploaded_file)

    # 3. Basic Rename (Spaces to Underscores)
    df.columns = df.columns.str.replace(' ', '_')
    
    # 4. Advanced Rename (Recommended for SQL/Analysis)
    # This handles spaces, special chars like '/', and lowercases everything
    df.columns = [
        c.strip()
        .replace(' ', '_')
        .replace('/', '')
        .replace('%', 'pct')
        .lower() 
        for c in df.columns
    ]

    # 5. Drop the rows containing atleast 1 null value the CSV into a pandas DataFrame
    df = df.dropna(subset=['story_points_completed'])

    # 1. Connect to a database (creates it if it doesn't exist)
    conn = sqlite3.connect('Metrics.db')

    # 2. Create a cursor object to execute commands
    cursor = conn.cursor()

    # This creates the table 'new_table' automatically from your df
    df.to_sql('Indicators', conn, if_exists='replace', index=False)


    # 6. Fetch and display data
    cursor.execute('SELECT * FROM Indicators')
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    # 7. Close the connection when finished
    conn.close()


    with sqlite3.connect('Metrics.db') as conn:
        # This single line handles the query AND the formatting
        dfsql = pd.read_sql_query("SELECT * FROM Indicators", conn)
        
    conn.close()

    # 3. Display the DataFrame
    st.write("### Data Preview")
    st.dataframe(df) # Interactive table