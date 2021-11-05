import pandas as pd
import streamlit as st
import streamlit_theme as stt
from sqlalchemy import create_engine
import psycopg2 as db
import numpy as np
import os
from matplotlib import pyplot as plt
import seaborn as sns
pd.set_option('display.max_colwidth', None)


st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title('Virginia Court System')
stt.set_theme({'primary': '#1b3388'})




@st.cache(persist= True)  
def load_data():
    # connect to db
    postPass=os.environ["POSTGRES_PASS"]
    try:
        conn = db.connect(host='localhost', database='expunge', user='jupyter', password=postPass, port='5432')
    except:
        print("I am unable to connect to the database") 

    cur = conn.cursor()
    try:
        tables=cur.execute("select * from pg_catalog.pg_tables WHERE schemaname != 'information_schema' AND schemaname != 'pg_catalog';")
        print(cur)
    
    except:
        print("I can't drop our test database!")
    
    # load data 
    myquery = """
    SELECT * FROM public.expunge LIMIT 5000
    """
    df = pd.read_sql(myquery, con=conn)
#     print(f"courtdata: {df}")

    replace_map = {'Black(Non-Hispanic)':'Black (Non-Hispanic)', 
                   'White Caucasian(Non-Hispanic)':'White (Non-Hispanic)', 
                   'Other(Includes Not Applicable.. Unknown)':'Other',
                   'White Caucasian (Non-Hispanic)':'White (Non-Hispanic)',
                   'Unknown (Includes Not Applicable.. Unknown)':'Other', 
                   'NA':'Other',
                   'Asian Or Pacific Islander':'Asian or Pacific Islander', 
                   'Black (Non-Hispanic)':'Black (Non-Hispanic)', 
                   'White':'White (Non-Hispanic)',
                   'American Indian':'American Indian or Alaskan Native', 
                   'Unknown':'Other',
                   'Other (Includes Not Applicable.. Unknown)':'Other', 
                   'Black':'Black (Non-Hispanic)',
                   'American Indian or Alaskan Native':'American Indian or Alaskan Native',
                   'American Indian Or Alaskan Native':'American Indian or Alaskan Native', 
                   'Asian or Pacific Islander':'Asian or Pacific Islander'}
    df.Race = df.Race.replace(replace_map)


    return df



def crosstab_melt(df, noll=False):
    if noll:
        col = "expungable_no_lifetimelimit"
    else:
        col = "expungable"
    rowtable = (pd.crosstab(df.Race, df[col], normalize='index')*100).round(2).reset_index()
    barplot = pd.melt(rowtable,
                      id_vars = ['Race'],
                      value_vars = ['Automatic', 'Automatic (pending)','Not eligible', 'Petition', 'Petition (pending)'])
    return barplot

    
def main():
    menu = ["Home"]
    
#     options = st.multiselect(
#         'what '
#     )
#     options = st.multiselect(
#      'What are your favorite colors',
#      ['Green', 'Yellow', 'Red', 'Blue'],
#      ['Yellow', 'Red'])
#     st.write('You selected:', options)
    
    choice = st.sidebar.selectbox("Home", menu)
    
    if choice == 'Home':
        st.subheader('Home')
        df = load_data()
        
        if st.checkbox('Show dataframe'):
            st.write(df)

            
        st.title("**♟**Expungability by Race**♟**")
        st.write("Here, you can see the breakdown of expungability based on race.")
        
        
#         df_true = df[df['lifetime']=="TRUE"]
#         df_false = df[df['lifetime']=="FALSE"]
        
        
#         barplot_true = crosstab_melt(df_true)
#         barplot_false = crosstab_melt(df_false)
        
        

        

#         plt.figure(figsize=(24, 6))
#         sns.barplot(x='Race', y='value', hue='expungable', data=barplot)    
#         st.pyplot(plt)

        
#         # let the user choose to see the dataframe, default is hiden
#         if st.checkbox('Show dataframe'):
#             st.write(rowtable)

            
            
        st.subheader("Plotly")
        
        # would love to make this a plotly graph but having some trouble with the grouping 
        import plotly.express as px
        
        copDF = df.copy()
        
        if st.checkbox('Same Day Rule in Effect'):
            barplot = crosstab_melt(copDF, noll=True)
            fig = px.bar(barplot, x="Race", y="value", color='expungable_no_lifetimelimit', barmode='group')
        else: 
            barplot = crosstab_melt(copDF)
            fig = px.bar(barplot, x="Race", y="value", color='expungable', barmode='group')
        st.plotly_chart(fig)
   
        
#         # now going to add a slider to toggle between lifetime
#         import plotly.express as px
#         fig = px.scatter(barplot, x="Race", y="value", animation_frame=df.lifetime, animation_group="Race",
#                    size="value", color="expungable")
# #                          hover_name="country",
# #                    log_x=True, size_max=55, range_x=[100,100000], range_y=[25,90])
#         fig["layout"].pop("updatemenus") # optional, drop animation buttons
#         fig.show()
            
            
            
    else:
        st.error('Something is wrong')

if __name__ == '__main__':
    main()