# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import pandas as pd

# Write directly to the app
st.title("🥤Customize Your Smoothie!🥤")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the Snowflake Dataframe to a pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections = 5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chose in ingredients_list:
        ingredients_string += fruit_chose + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chose, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chose,' is ', search_on, '.')

        st.subheader(fruit_chose + ' Nutrition Information')
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")  
        st_df = st.dataframe(data = fruityvice_response.json(), use_container_width = True)

    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    # '""" + ingredients_string + """', 

    # st.write(my_insert_stmt)
    
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")




        
