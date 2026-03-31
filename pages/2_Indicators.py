
import sqlite3
import pandas as pd
import streamlit as st

# ... (Previous connection and filter code) ...

st.set_page_config(layout="wide",
                   
    page_title="Metrics Data Analytics")

# 1. Setup Layout (This defines main_body)
spacer_left, main_body, spacer_right = st.columns([1, 8, 1])

with main_body:
    st.divider()
    st.subheader("💡 Key Metrics Insights")
    
    # 1. Define the questions in a dictionary (Question: SQL Query)
   # 1. Define the questions in a dictionary (Question: SQL Query)
business_questions = {
    "Select a question to analyze...": None,

    "1. Which squads have the highest average team morale? \nBusiness Value: Identifies healthy team cultures and potential leadership benchmarks.": 
        "SELECT Initiative, squad, ROUND(AVG(team_moral), 2) as Avg_Morale FROM Indicators WHERE team_moral IS NOT NULL GROUP BY squad ORDER BY Avg_Morale DESC",

    "2. Which sprints show a critical 'Red' completion status despite high utilization? \nBusiness Value: Highlights inefficiencies or over-commitment issues.": 
        "SELECT sprint, squad, actual_team_utilization, sprint_completion_pct FROM Indicators WHERE Sprint_Completion_pct_Calc = 'Red' AND actual_team_utilization > 85",

    "3. Is there a correlation between team morale and sprint completion percentage? \nBusiness Value: Validates the impact of employee engagement on productivity.": 
        "SELECT team_moral, ROUND(AVG(sprint_completion_pct), 2) as Avg_Completion FROM Indicators WHERE team_moral IS NOT NULL GROUP BY team_moral ORDER BY team_moral DESC",

    "4. What is the average velocity for each squad across all product increments? \nBusiness Value: Establishes a baseline for future capacity planning.": 
        "SELECT squad, ROUND(AVG(story_points_completed), 2) as Avg_Velocity FROM Indicators WHERE story_points_completed IS NOT NULL GROUP BY squad",

    "5. Which product increments (PI) are currently lacking data (NaN values)? \nBusiness Value: Identifies gaps in reporting and operational compliance.": 
        "SELECT product_increment, squad, COUNT(*) as Missing_Data_Rows FROM Indicators WHERE team_moral IS NULL GROUP BY product_increment, squad",

    "6. How does squad turnover affect story point delivery? \nBusiness Value: Quantifies the cost of attrition on project timelines.": 
        "SELECT turnover, AVG(story_points_completed) as Avg_Points FROM Indicators GROUP BY turnover ORDER BY turnover ASC",

    "7. Which squads are consistently 'Over-Utilized' (Utilization > 90%)? \nBusiness Value: Alerts management to potential burnout risks.": 
        "SELECT squad, COUNT(sprint) as Over_Utilized_Sprints FROM Indicators WHERE actual_team_utilization > 90 GROUP BY squad",

    "8. Which initiatives have the highest percentage of 'Green' status across all metrics? \nBusiness Value: Measures overall initiative health and success rates.": 
        "SELECT initiative, COUNT(*) as Green_Metrics FROM Indicators WHERE Sprint_Completion_pct_Calc = 'Green' AND team_moral_calc = 'Green' GROUP BY initiative",

    "9. Are there any squads where the average velocity is significantly lower than 20 points? \nBusiness Value: Identifies underperforming teams needing support or re-scoping.": 
        "SELECT squad, AVG(story_points_completed) as Low_Velocity FROM Indicators GROUP BY squad HAVING Low_Velocity < 20",

    "10. Which locations/initiatives are experiencing the most 'Amber' or 'Red' morale ratings? \nBusiness Value: Directs HR and leadership interventions to specific areas.": 
        "SELECT initiative, COUNT(*) as Warning_Count FROM Indicators WHERE team_moral_calc IN ('Amber', 'Red') GROUP BY initiative",

    "11. Does a larger squad size result in higher story point completion? \nBusiness Value: Analyzes the ROI of adding more members to a squad.": 
        "SELECT squad_members, AVG(story_points_completed) as Avg_Delivery FROM Indicators WHERE squad_members IS NOT NULL GROUP BY squad_members",

    "12. Which sprints achieved 90 percent completion but were still flagged as 'Red' or 'Amber'? \nBusiness Value: Audits the logic of the 'Calc' columns for consistency.": 
        "SELECT sprint, squad, sprint_completion_pct, Sprint_Completion_pct_Calc FROM Indicators WHERE sprint_completion_pct >= 90 AND Sprint_Completion_pct_Calc != 'Green'",

}


    # 2. The Dropdown List
selected_q = st.selectbox("Choose a Metrics Question:", options=list(business_questions.keys()))

    # 3. Run the logic when a question is picked
if selected_q and business_questions[selected_q]:
    with sqlite3.connect('Metrics.db') as conn:
            insight_df = pd.read_sql_query(business_questions[selected_q], conn)
            
            # Format booleans for insights too
            for col in insight_df.columns:
                if insight_df[col].dtype == 'int64' and insight_df[col].dropna().isin([0, 1]).all():
                    insight_df[col] = insight_df[col].map({1: 'Yes', 0: 'No'})

            # Display the insight table
            st.write(f"**Analysis for:** {selected_q}")
            st.dataframe(insight_df, use_container_width=True, hide_index=True)

