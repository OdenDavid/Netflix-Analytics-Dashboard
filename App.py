"""
In an environment with streamlit installed,
Run with `streamlit run App.py`
"""

import pandas as pd
import streamlit as st
from PIL import Image

import sqlite3

from Helper import *

# ============= PAGE SETUP ============
st.set_page_config(page_title="Charty Netflix", page_icon="📊", layout="wide")

c1, c2 = st.columns([7,3])
with c1:
    st.subheader("Netflix Analytics Interactive Dashboard")
with c2:
    years = [str(year) for year in range(2020, 1961, -1)]
    years.insert(0,"All")
    year = st.selectbox(
    'Filter by release year',options=years, index=0)


# =========== Initialize SQL ==========
conn = sqlite3.connect("Data.db") # db - database
cursor_object = conn.cursor() # Cursor object

# ============= Or Read Data using pandas ========
if year == "All":
    data = pd.read_sql_query("""SELECT * FROM Netflix;""", conn)
else:
    data = pd.read_sql_query("""SELECT * FROM Netflix
                                WHERE release_year={};""".format(year), conn)

#image = Image.open('Images/logo.png')
#st.image(image)

# ================== Row 1: Count plots =====================
col1,col2,col3,col4,col5,col6 = st.columns(6)
with col1:
    totalshows = counts("totalshows", filteryear=year, cursor=cursor_object) # Total Number of Shows
    plot_metric(label="Total Shows",value=totalshows)

with col2:
    totalmovies = counts("totalmovies", filteryear=year, cursor=cursor_object) # Number of Movies
    plot_metric(label="Movies",value=totalmovies)

with col3:
    totaltvshows = counts("totaltvshows", filteryear=year, cursor=cursor_object) # Number of TV Shows
    plot_metric(label="Tv Shows",value=totaltvshows)

with col4:
    genres = counts("genres",year,data=data) # Number of Unique Genres
    plot_metric(label="Number of Genres",value=genres)

with col5:
    directors = counts("directors",data=data) # Number of Directors
    plot_metric(label="Directors",value=totalshows)

with col6:
    countries = counts("countries",data=data) # Number of Countries Represented
    plot_metric(label="Number of Countries",value=countries)

st.write('---')

# ================== Row 2: Plots =====================
col1,col2,col3 = st.columns(3)
with col1:
    st.caption(unsafe_allow_html=True,body="<b>Distribution of Show Types</b>")
    pie_chart(cursor=cursor_object,filteryear=year)

with col2:
    image = Image.open('imager.jpeg')
    st.image(image)

with col3:
    st.caption(unsafe_allow_html=True,body="<b>Most Common Words in Descriptions</b>")
    wordcloud(data=data)

st.write('---')

# ================== Row 3: Plots =====================
col1,col2 = st.columns(2)
with col1:
    st.caption(unsafe_allow_html=True,body="<b>Rating Distribution of Shows</b>")
    rating_bar(data=data)
with col2:
    st.caption(unsafe_allow_html=True,body="<b>Monthly Addition of Shows to Netflix Over Time</b>")
    show_additions(data=data)

st.write('---')

# ================== Row 4: Plots =====================
col1,col2 = st.columns(2)
with col1:
    st.caption(unsafe_allow_html=True,body="<b>Top 20 Casts Based on Number of Shows</b>")
    casts_bar(data=data)
with col2:
    st.caption(unsafe_allow_html=True,body="<b>Top 20 Directors Based on Number of Shows</b>")
    directors_bar(data=data)

st.write('---')

# ================== Row 5: Tree map =====================
st.caption(unsafe_allow_html=True,body="<b>Distribution of Shows Based on Genres</b>")
tree_map(data=data)

st.write('---')

# ================== Row 6: Map =====================
st.caption(unsafe_allow_html=True,body="<b>Count of Shows by Country</b>")
country_map(data=data)












