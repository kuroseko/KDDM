import pandas as pd
import streamlit as st
from collections import defaultdict

# Load the data
df = pd.read_excel("C:/Users/User/Desktop/kddm/JapanMenuItems.xlsx")
n_samples, n_features = df.shape
features = ["California Roll", "Salmon Nigiri", "Tonkotsu Ramen", "Chicken Teriyaki Bento",
            "Edamame", "Gyoza (Dumplings)", "Tempura (Shrimp)", "Green Tea Ice Cream",
            "Mochi Ice Cream", "Matcha Latte"]

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

# Streamlit App
st.title('Association Rules Analysis')

# Display the rules
st.subheader('Rules sorted in descending order based on confidence')
for premise, conclusion in sorted(confidence, key=lambda x: confidence[x], reverse=True):
    premise_name = features[premise]
    conclusion_name = features[conclusion]
    st.write(f"Rule: If a person buys {premise_name}, they will also buy {conclusion_name}")
    st.write(f"- Confidence: {confidence[(premise, conclusion)]:.3f}")
    st.write(f"- Support: {support[(premise, conclusion)]}")

# Optionally, you can add more Streamlit components such as sliders, text inputs, etc.
