# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)
cnx=st.connection("snowflake")
session=cnx.session()
#session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    
    # st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        # New section
# New section to display smoothiefroot nutrition information
#import requests
#smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# st.text(smoothiefroot_response.json())
#sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

# New section to display smoothiefroot nutrition information
import requests

# 1. Add headers to mimic a standard browser profile
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# 2. Pass the headers argument into your get request
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon", headers=headers)

# 3. Render the dataframe container safely
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)



# Fetch the nutrition payload safely
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

# Validate the server response is an HTTP 200 OK and contains content
if smoothiefroot_response.status_code == 200 and smoothiefroot_response.text.strip():
    try:
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    except requests.exceptions.JSONDecodeError:
        st.error("The API returned a response, but it was not valid JSON.")
        st.text(smoothiefroot_response.text) # Display what the server actually sent
else:
    st.warning(f"Unable to fetch nutrition data. Server status code: {smoothiefroot_response.status_code}")
