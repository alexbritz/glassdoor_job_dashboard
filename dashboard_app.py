import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# Load and Clean the Data
# @st.cache  # This function will be cached
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
    
    # Clean: Extract Job Title
    def extract_job_title(job_title_text):
        return job_title_text.split('(')[0].strip()
    data['Job Title'] = data['Job Title'].apply(lambda x: extract_job_title(x))

    # Clean: Summarize Similar Job Titles
    def categorize_title(title):
        category_mapping = {
            "Data Scientist": "Data Scientist",
            "Senior": "Senior Data Scientist",
            "Sr": "Senior Data Scientist",
            "Junior": "Junior Data Scientist",
            "Jr": "Junior Data Scientist",
            "Entry Level": "Junior Data Scientist",
            "Principal": "Principal/Lead Data Scientist",
            "Lead": "Principal/Lead Data Scientist",
            "Data Engineer": "Data Engineer",
            "Machine Learning": "Machine Learning Specialist",
            "Manager": "Manager/Director",
            "Director": "Manager/Director",
            "Analyst": "Analyst"
        }

        if "Machine Learning" in title:
            return "Machine Learning Specialist"
        
        for key, value in category_mapping.items():
            if key in title:
                return value
        return "Other"

    def recategorize_title(row):
        if row['Job Category'] == 'Data Scientist':
            if any(keyword in row['Cleaned Job Title'] for keyword in ["Junior", "Entry Level"]):
                return "Junior Data Scientist"
            elif any(keyword in row['Cleaned Job Title'] for keyword in ["Senior", "Sr"]):
                return "Senior Data Scientist"
            elif any(keyword in row['Cleaned Job Title'] for keyword in ["Principal", "Lead"]):
                return "Principal/Lead Data Scientist"
            elif any(keyword in row['Cleaned Job Title'] for keyword in ["Manager", "Director"]):
                return "Manager/Director"
        return row['Job Category']

    # Function that cleans the job title
    def clean_title(df):
        df['Cleaned Job Title'] = df['Job Title'].str.title()
        # Initial categorization
        df['Job Category'] = df['Job Title'].apply(categorize_title)
        # Recategorization based on specific keywords
        df['Job Category'] = df.apply(recategorize_title, axis=1)
        return df

    data = clean_title(data)

    data['Mean Salary Estimate'] = data[['Min Salary Estimate', 'Max Salary Estimate']].mean(axis=1)
    data['Mean Salary Estimate MUSD'] = data['Mean Salary Estimate']/1000

    return data

# Load your data
data = load_and_clean_data()

# Streamlit App
st.title("Salary Estimates vs. Company Rating by Job Title")

# Generate and sort job title counts
title_counts = data["Job Category"].value_counts().reset_index()
title_counts.columns = ['Job Category', 'Count']
title_counts['Dropdown'] = title_counts['Job Category'] + " (" + title_counts['Count'].astype(str) + ")"

# Dropdown: Select Job Title with Counts
selected_title_with_count = st.selectbox("Select Job Category", options=title_counts['Dropdown'])

# Extract job title from selection
selected_title = selected_title_with_count.split(" (")[0]

# Filter data based on selected job title
filtered_data = data[data["Job Category"] == selected_title]

# Scatter Plot: Salary Estimates vs. Company Rating
fig = px.scatter(filtered_data, 
                 x='Company Rating', 
                 y=['Min Salary Estimate', 'Max Salary Estimate'], 
                 title=f'Salary Estimates vs. Company Rating for {selected_title}')
st.plotly_chart(fig)# Display the plot

# Pie chart for job distribution
job_distribution = data['Job Category'].value_counts()
fig_jobs = px.pie(job_distribution, values=job_distribution.values, names=job_distribution.index, title="Job Distribution")
st.plotly_chart(fig_jobs)


# Dropdown menu for job distribution selection
options = list(job_distribution.index) + ['All']
selected_option = st.selectbox('Select a Job Category:', options)

# Filter data based on selected job category
if selected_option != 'All':
    filtered_data = data[data['Job Category'] == selected_option]
else:
    filtered_data = data

# Overlapping histograms for Min and Max Salary Estimates with distinct colors for the filtered data
fig_histogram = go.Figure()
fig_histogram.add_trace(go.Histogram(x=filtered_data['Min Salary Estimate'], name='Min Salary Estimate', opacity=0.7, marker_color='blue'))
fig_histogram.add_trace(go.Histogram(x=filtered_data['Max Salary Estimate'], name='Max Salary Estimate', opacity=0.7, marker_color='orange'))
fig_histogram.update_layout(barmode='overlay', title=f"Distribution of Min and Max Salary Estimates for {selected_option} Category", xaxis_title="Salary ($)", yaxis_title="Count")
st.plotly_chart(fig_histogram)

