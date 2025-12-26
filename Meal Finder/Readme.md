# Gluten & Potato Starch Free Meal Finder App

A Python Streamlit application for searching and discovering meal options that are both gluten-free and potato starch-free.

## Features

- **Multi-Category Browsing**: Search across 12 food categories including dairy, proteins, grains, snacks, and more
- **Smart Filtering**: 
  - Filter by food category
  - Search by brand name
  - Filter by certifications (Organic, Non-GMO, etc.)
  - Exclude specific allergens (dairy, eggs, soy, tree nuts, peanuts, fish)
- **Meal Planning**: Quick filters for breakfast, lunch, dinner, snacks, or baking/cooking
- **Detailed Information**: View complete ingredients lists, allergen statements, and certifications for each product
- **Meal Ideas**: Built-in suggestions for quick meal planning

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure the JSON database file is in the same directory:**
   - The app requires `gluten_potato_starch_free_foods.json` to be in the same folder as `meal_finder_app.py`

## Usage

### Running the App

1. **Navigate to the app directory:**
   ```bash
   cd /path/to/app/directory
   ```

2. **Start the Streamlit app:**
   ```bash
   streamlit run meal_finder_app.py
   ```

3. **Access the app:**
   - The app will automatically open in your default web browser
   - If not, navigate to `http://localhost:8501`

### Using the App

#### Sidebar Filters
- **Select Food Categories**: Choose which categories to display (dairy, proteins, snacks, etc.)
- **Search by Brand**: Type a brand name to filter results
- **Filter by Certifications**: Show only products with specific certifications
- **Exclude Allergens**: Check boxes to exclude products containing specific allergens
- **Meal Planning**: Select a meal type for targeted suggestions

#### Main Display
- Products are organized by category in tabs
- Click on any product to expand and see:
  - Complete ingredients list
  - Allergen statement
  - Certifications
  - Gluten-free and potato starch-free verification

#### Meal Ideas
- Scroll to the bottom for quick meal inspiration
- Ideas organized by breakfast, lunch, and dinner

## Database Structure

The app uses a JSON database with the following structure:
```json
{
  "foods": [
    {
      "category": "Category Name",
      "items": [
        {
          "brand": "Brand Name",
          "product_name": "Product Name",
          "ingredients": ["ingredient1", "ingredient2"],
          "allergen_statement": "Allergen information",
          "certifications": ["Cert1", "Cert2"],
          "gluten_free": true,
          "potato_starch_free": true
        }
      ]
    }
  ]
}
```

## Customization

### Adding New Products
Edit the `gluten_potato_starch_free_foods.json` file to add new products following the structure above.

### Modifying Meal Suggestions
Edit the "Quick Meal Ideas" section in `meal_finder_app.py` (lines ~180-210) to customize meal suggestions.

## Important Notes

- ⚠️ **Always verify product labels** before consuming, as formulations may change
- This app is for informational purposes only
- The database currently contains 48 products across 12 categories
- All listed products are verified to be both gluten-free and potato starch-free

## Troubleshooting

### Common Issues

**"Food database file not found" error:**
- Ensure `gluten_potato_starch_free_foods.json` is in the same directory as the app
- Check that the filename is spelled correctly

**App won't start:**
- Verify Python 3.8+ is installed: `python --version`
- Ensure Streamlit is installed: `pip list | grep streamlit`
- Try reinstalling requirements: `pip install -r requirements.txt --upgrade`

**Port already in use:**
- Streamlit default port is 8501
- Use a different port: `streamlit run meal_finder_app.py --server.port 8502`

## Support

For issues or questions about the app, please check:
- Streamlit documentation: https://docs.streamlit.io
- Python documentation: https://docs.python.org

## Version
- App Version: 1.0
- Database Version: 1.0
- Last Updated: 2025-12-26
