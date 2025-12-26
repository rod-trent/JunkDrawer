import streamlit as st
import json
import pandas as pd
from collections import defaultdict

# Page configuration
st.set_page_config(
    page_title="Gluten & Potato Starch Free Meal Finder",
    page_icon="🍽️",
    layout="wide"
)

# Load the JSON data
@st.cache_data
def load_food_data():
    with open('gluten_potato_starch_free_foods.json', 'r') as f:
        data = json.load(f)
    return data

# Load data
try:
    food_data = load_food_data()
    foods = food_data['foods']
except FileNotFoundError:
    st.error("Food database file not found. Please ensure 'gluten_potato_starch_free_foods.json' is in the same directory.")
    st.stop()

# Title and description
st.title("🍽️ Gluten & Potato Starch Free Meal Finder")
st.markdown("*Find safe, delicious meal options without gluten or potato starch*")
st.divider()

# Sidebar filters
st.sidebar.header("🔍 Search Filters")

# Category filter
all_categories = [category['category'] for category in foods]
selected_categories = st.sidebar.multiselect(
    "Select Food Categories",
    options=all_categories,
    default=all_categories
)

# Brand search
brand_search = st.sidebar.text_input("Search by Brand", "")

# Certification filter
all_certifications = set()
for category in foods:
    for item in category['items']:
        all_certifications.update(item.get('certifications', []))

selected_certifications = st.sidebar.multiselect(
    "Filter by Certifications",
    options=sorted(list(all_certifications)),
    default=[]
)

# Allergen exclusion
st.sidebar.subheader("🚫 Exclude Allergens")
exclude_dairy = st.sidebar.checkbox("Exclude Dairy/Milk")
exclude_eggs = st.sidebar.checkbox("Exclude Eggs")
exclude_soy = st.sidebar.checkbox("Exclude Soy")
exclude_tree_nuts = st.sidebar.checkbox("Exclude Tree Nuts")
exclude_peanuts = st.sidebar.checkbox("Exclude Peanuts")
exclude_fish = st.sidebar.checkbox("Exclude Fish")

# Meal planning section
st.sidebar.divider()
st.sidebar.header("🍱 Meal Planning")
meal_type = st.sidebar.selectbox(
    "I'm planning...",
    ["Browse All", "Breakfast", "Lunch", "Dinner", "Snack", "Baking/Cooking"]
)

# Function to check if item matches allergen exclusions
def passes_allergen_filter(item):
    allergen_statement = item.get('allergen_statement', '').lower()
    
    if exclude_dairy and ('milk' in allergen_statement or 'dairy' in allergen_statement):
        return False
    if exclude_eggs and 'egg' in allergen_statement:
        return False
    if exclude_soy and 'soy' in allergen_statement:
        return False
    if exclude_tree_nuts and 'tree nut' in allergen_statement:
        return False
    if exclude_peanuts and 'peanut' in allergen_statement:
        return False
    if exclude_fish and 'fish' in allergen_statement:
        return False
    
    return True

# Function to filter items based on meal type
def filter_by_meal_type(category_name, meal_type):
    if meal_type == "Browse All":
        return True
    
    meal_mappings = {
        "Breakfast": ["Breakfast Foods", "Dairy Products", "Beverages"],
        "Lunch": ["Proteins", "Vegetables & Fruits", "Pasta & Noodles", "Legumes & Beans", "Condiments & Sauces"],
        "Dinner": ["Proteins", "Vegetables & Fruits", "Pasta & Noodles", "Legumes & Beans", "Grains & Flours", "Condiments & Sauces"],
        "Snack": ["Snacks", "Nuts & Seeds", "Dairy Products", "Beverages"],
        "Baking/Cooking": ["Baking Ingredients", "Grains & Flours", "Condiments & Sauces"]
    }
    
    return category_name in meal_mappings.get(meal_type, [])

# Filter and display results
filtered_results = []

for category in foods:
    if category['category'] not in selected_categories:
        continue
    
    if not filter_by_meal_type(category['category'], meal_type):
        continue
    
    for item in category['items']:
        # Brand filter
        if brand_search and brand_search.lower() not in item['brand'].lower():
            continue
        
        # Certification filter
        if selected_certifications:
            item_certs = item.get('certifications', [])
            if not any(cert in item_certs for cert in selected_certifications):
                continue
        
        # Allergen filter
        if not passes_allergen_filter(item):
            continue
        
        filtered_results.append({
            'category': category['category'],
            'item': item
        })

# Display results
st.subheader(f"📋 Found {len(filtered_results)} Products")

if len(filtered_results) == 0:
    st.warning("No products match your current filters. Try adjusting your search criteria.")
else:
    # Group results by category
    results_by_category = defaultdict(list)
    for result in filtered_results:
        results_by_category[result['category']].append(result['item'])
    
    # Display tabs for each category
    tabs = st.tabs(list(results_by_category.keys()))
    
    for tab, (category_name, items) in zip(tabs, results_by_category.items()):
        with tab:
            for item in items:
                with st.expander(f"**{item['brand']}** - {item['product_name']}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**Ingredients:**")
                        ingredients_list = ", ".join(item['ingredients'])
                        st.write(ingredients_list)
                        
                        st.markdown("**Allergen Statement:**")
                        st.info(item['allergen_statement'])
                    
                    with col2:
                        st.markdown("**Certifications:**")
                        for cert in item.get('certifications', []):
                            st.markdown(f"✓ {cert}")
                        
                        st.markdown("**Status:**")
                        st.success("✓ Gluten-Free")
                        st.success("✓ Potato Starch-Free")

# Meal suggestion section
st.divider()
st.subheader("💡 Quick Meal Ideas")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🌅 Breakfast Ideas")
    st.markdown("""
    - **Simple Bowl**: Gluten-free oats + almond butter + fresh berries
    - **Protein Start**: Greek yogurt + chia seeds + honey
    - **Pancake Morning**: Almond flour pancakes + pure maple syrup
    """)

with col2:
    st.markdown("### 🥗 Lunch Ideas")
    st.markdown("""
    - **Power Bowl**: Quinoa + grilled chicken + roasted vegetables
    - **Light & Fresh**: Tuna salad on rice crackers + side of fruit
    - **Pasta Dish**: Brown rice pasta + turkey + tomato sauce
    """)

with col3:
    st.markdown("### 🍽️ Dinner Ideas")
    st.markdown("""
    - **Classic Comfort**: Chicken breast + sweet peas + brown rice
    - **Mediterranean**: Chickpea pasta + olive oil + fresh vegetables
    - **Simple & Hearty**: Black beans + rice + cheddar cheese
    """)

# Footer
st.divider()
st.caption("⚠️ Always verify product labels before consuming, as formulations may change. This app is for informational purposes only.")
st.caption(f"📊 Database contains {food_data['metadata']['total_items']} products across {food_data['metadata']['categories']} categories")
