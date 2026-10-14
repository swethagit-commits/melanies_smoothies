import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# 1. App Titles and Headings
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# 2. Customer Name Input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# 3. Fetch Fruit Options from Snowflake Table
session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# 4. Multi-Select Dropdown Component (Max 5 items)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# 5. Process Selection and Fetch Nutrition Data
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        st.subheader(f'{fruit_chosen} Nutrition Information')
        
        # Safe API Request Call to the Public Fruityvice Endpoint
        try:
            # Replaced private ://smoothiefroot.com with the working public API
            fruityvice_response = requests.get(f"https://fruityvice.com{fruit_chosen}", timeout=5)
            
            if fruityvice_response.status_code == 200:
                fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
            else:
                st.warning(f"Could not load nutrition details for {fruit_chosen}. (Status: {fruityvice_response.status_code})")
                
        except Exception as e:
            st.error(f"Nutrition API connection timed out for {fruit_chosen}.")

    # 6. Build the SQL Insert command
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
    
    # 7. Submit Action Button
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        if name_on_order.strip():
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        else:
            st.error("Please enter a name before submitting your smoothie order.")
