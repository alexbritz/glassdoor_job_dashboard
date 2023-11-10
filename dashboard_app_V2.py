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

    def extract_salary_min_max(salary_text):
        salary_match = re.findall(r'\$(\d+)[Kk]', salary_text)
        if len(salary_match) == 1:
            return [int(salary_match[0]), int(salary_match[0])]
        elif len(salary_match) == 2:
            return [int(salary_match[0]), int(salary_match[1])]
        else:
            return [-1, -1]
    
    data[['Min Salary Estimate', 'Max Salary Estimate']] = data['Salary Estimate'].apply(lambda x: pd.Series(extract_salary_min_max(x)))
    
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

    #
    category_mapping = {
            "Data Scientist": "Data Scientist",
            "Data Science": "Data Scientist",
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
            "Analyst": "Analyst",
            "Database Administrator": "Database Administrator"
        }
    
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
    data['Job Category'] = 'Other'

    for key in category_mapping.keys():
        data.loc[data['Job Title'].str.contains(key, flags=re.IGNORECASE), 'Job Category'] = category_mapping[key]

    data['Mean Salary Estimate'] = data[['Min Salary Estimate', 'Max Salary Estimate']].mean(axis=1)
    data['Mean Salary Estimate MUSD'] = data['Mean Salary Estimate']/1000

    return data

# Load your data
data = load_and_clean_data()

# Streamlit App
# st.title("Salary Estimates vs. Company Rating by Job Title")
st.markdown('<h1 style="font-size: 24px;">Glassdoor Data Science Jobs</h1>', unsafe_allow_html=True)

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

