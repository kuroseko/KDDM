import pandas as pd
import streamlit as st
from collections import defaultdict
import requests
from io import BytesIO

# Function to process the file from GitHub
def process_github_file(repo_url, file_path):
    raw_url = f"{repo_url}/raw/main/{file_path}"
    response = requests.get(raw_url)
    if response.status_code == 200:
        content = BytesIO(response.content)
        df = pd.read_excel(content)
        n_samples, n_features = df.shape
        features = list(df.columns)

        # Compute rules
        valid_rules = defaultdict(int)
        invalid_rules = defaultdict(int)
        num_occurrences = defaultdict(int)

        for index, row in df.iterrows():
            for premise in range(n_features):
                if row[premise] == 0:
                    continue
                num_occurrences[premise] += 1
                for conclusion in range(n_features):
                    if premise == conclusion:
                        continue
                    if row[conclusion] == 1:
                        valid_rules[(premise, conclusion)] += 1
                    else:
                        invalid_rules[(premise, conclusion)] += 1

        support = valid_rules
        confidence = defaultdict(float)
        for premise, conclusion in valid_rules.keys():
            confidence[(premise, conclusion)] = valid_rules[(premise, conclusion)] / num_occurrences[premise]

        return confidence, support, features
    else:
        st.error("Failed to fetch file from GitHub repository.")
        return None, None, None

# Streamlit App
st.title('Item Recommendation')

# GitHub repository URL and file path
repo_url = "https://github.com/kuroseko/KDDM"
file_path = "JapanMenuItems.xlsx"

# Process the file from GitHub
confidence, support, features = process_github_file(repo_url, file_path)

# Display dropdown menu to select menu item
if confidence is not None:
    selected_item = st.selectbox('Select a menu item:', features)

    recommendations = []
    for premise, conclusion in sorted(confidence, key=lambda x: confidence[x], reverse=True):
        premise_name = features[premise]
        conclusion_name = features[conclusion]
        if premise_name == selected_item:
            recommendations.append(conclusion_name)
        if len(recommendations) >= 3:
            break

    if recommendations:
        st.subheader(f'Top 3 recommended items to go with {selected_item}:')
        for i, item in enumerate(recommendations, start=1):
            st.write(f"{i}. {item}")
    else:
        st.write("No recommendations available for the selected item.")
