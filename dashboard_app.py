import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Load and Clean the Data
@st.cache  # This function will be cached
def load_and_clean_data():
    # Load
    data = pd.read_csv('glassdoor_jobs.csv')
    
    # Clean: Extract Min and Max Salary Estimate
    def extract_salary(salary_text):
        salary_match = re.findall(r'\$(\d+)[Kk]', salary_text)
        return [int(salary_match[0]), int(salary_match[1])] if salary_match and len(salary_match) == 2 else [-1, -1]
    data[['Min Salary Estimate', 'Max Salary Estimate']] = data['Salary Estimate'].apply(lambda x: pd.Series(extract_salary(x)))
    
    # Clean: Extract Company Name and Rating
    def extract_company_info(company_text):
        split_text = company_text.split('\n')
        return [split_text[0], float(split_text[1])] if len(split_text) == 2 else [company_text, -1]
    data[['Company Name Clean', 'Company Rating']] = data['Company Name'].apply(lambda x: pd.Series(extract_company_info(x)))
    
    return data

# Load your data
data = load_and_clean_data()

# Streamlit App
st.title("Salary Estimates vs. Company Rating by Job Title")

# Generate and sort job title counts
title_counts = data["Job Title"].value_counts().reset_index()
title_counts.columns = ['Job Title', 'Count']
title_counts['Dropdown'] = title_counts['Job Title'] + " (" + title_counts['Count'].astype(str) + ")"

# Dropdown: Select Job Title with Counts
selected_title_with_count = st.selectbox("Select Job Title", options=title_counts['Dropdown'])

# Extract job title from selection
selected_title = selected_title_with_count.split(" (")[0]

# Filter data based on selected job title
filtered_data = data[data["Job Title"] == selected_title]

# Scatter Plot: Salary Estimates vs. Company Rating
fig = px.scatter(filtered_data, 
                 x='Company Rating', 
                 y=['Min Salary Estimate', 'Max Salary Estimate'], 
                 title=f'Salary Estimates vs. Company Rating for {selected_title}')

# Display the plot
st.plotly_chart(fig)
