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

# Initialize session state for selected item
if 'selected_item_name' not in st.session_state:
    st.session_state['selected_item_name'] = None

# Function to set the selected item in session state
def set_selected_item(item_name):
    st.session_state['selected_item_name'] = item_name

# Streamlit App
st.title('Item Recommendation')

# GitHub repository URL and file path
repo_url = "https://github.com/yourusername/yourrepo"
file_path = "JapanMenuItems.xlsx"

# Process the file from GitHub
confidence, support, features = process_github_file(repo_url, file_path)

# Dictionary of menu items with their image URLs
menu_items_with_images = {
    "California Roll": "https://norecipes.com/wp-content/uploads/2019/12/best-california-roll-004.jpg",
    "Salmon Nigiri": "https://aisforappleau.com/wp-content/uploads/2023/07/how-to-make-sushi-salmon-nigiri-6.jpg",
    "Tonkotsu Ramen": "https://www.seriouseats.com/thmb/IBikLAGkkP2QVaF3vLIk_LeNqHM=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/rich-and-creamy-tonkotsu-ramen-broth-from-scratch-recipe-Diana-Chistruga-hero-6d318fadcca64cc9ac3e1c40fc7682fb.JPG",
    "Chicken Teriyaki Bento": "https://images.squarespace-cdn.com/content/v1/63d0a16cfad8c1759df2fe31/54270454-daec-4ee8-95ac-77d58559b9b9/GCBC14_EP11_Chicken-Teriyaki-Bento-Box_1L0A7045-700x404.jpg",
    "Edamame": "https://images.services.kitchenstories.io/gwBULxPG7Q4QmFzkK_SoUCNJYKA=/3840x0/filters:quality(85)/images.kitchenstories.io/wagtailOriginalImages/R2958-final-photo-.jpg",
    "Gyoza (Dumplings)": "https://japanesetaste.com/cdn/shop/articles/how-to-make-gyoza-japanese-dumplings-at-home-japanese-taste.jpg?v=1694487043&width=5760",
    "Tempura (Shrimp)": "https://recipe30.com/wp-content/uploads/2022/11/Tempura-Shrimp.jpg",
    "Green Tea Ice Cream": "https://www.justonecookbook.com/wp-content/uploads/2021/08/Green-Tea-Ice-Cream-0099-I-1.jpg",
    "Mochi Ice Cream": "https://www.justonecookbook.com/wp-content/uploads/2020/08/Mochi-Ice-Cream-8680-I.jpg",
    "Matcha Latte": "https://cdn.loveandlemons.com/wp-content/uploads/2023/06/iced-matcha-latte.jpg",
    # ... more items and URLs as necessary
}


# Display buttons for each menu item using session state to track selection
st.subheader('Choose a menu item:')
for item_name, item_image_url in menu_items_with_images.items():
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button(f'Select {item_name}'):
            set_selected_item(item_name)
    with col2:
        st.image(item_image_url, caption=item_name, width=150)

# Display the recommendations if an item was selected
if st.session_state['selected_item_name']:
    selected_item = st.session_state['selected_item_name']
    st.write(f"Selected item: {selected_item}")
    st.subheader(f'Top 3 recommended items to go with {selected_item}:')
    recommendations = []

    # Logic to get recommendations based on the selected item
    for premise, conclusion in sorted(confidence, key=lambda x: confidence[x], reverse=True):
        premise_name = features[premise]
        conclusion_name = features[conclusion]
        if premise_name == selected_item and len(recommendations) < 3:
            recommendations.append(conclusion_name)

    # Display the recommendations
    for i, recommended_item in enumerate(recommendations, start=1):
        st.write(f"{i}. {recommended_item}")
