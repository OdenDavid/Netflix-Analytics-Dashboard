import streamlit as st
st.set_option('deprecation.showPyplotGlobalUse', False)
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from wordcloud import WordCloud
from wordcloud import STOPWORDS
import matplotlib.pyplot as plt


def plot_metric(label, value):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={
                "font.size": 25,
            },
            title={
                "text": label,
                "font": {"size": 16},
            },
        )
    )

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        margin=dict(t=30, b=0),
        showlegend=False,
        #plot_bgcolor="white",
        height=100,
    )

    st.plotly_chart(fig, use_container_width=True)

# ========== Row 1: Count plots ===========  
def counts(plot="", filteryear="", cursor=None, data=None):
    
    if plot == "totalshows": # Total Number of Shows
        if filteryear != "All":
            result = cursor.execute("""SELECT COUNT(*) AS total_shows
                                        FROM 'Netflix'
                                        WHERE release_year={};""".format(filteryear))
        else:
            result = cursor.execute("""SELECT COUNT(*) AS total_shows
                                        FROM 'Netflix';""")
        return result.fetchall()[0][0]
    
    elif plot == "totalmovies": # Number of Movies
        if filteryear != "All":
            result = cursor.execute("""SELECT COUNT(*) AS num_movies
                                        FROM 'Netflix'
                                        WHERE type = 'Movie' and release_year={};""".format(filteryear))
        else:
            result = cursor.execute("""SELECT COUNT(*) AS num_movies
                                        FROM 'Netflix'
                                        WHERE type = 'Movie';""")
        return result.fetchall()[0][0]

    elif plot == "totaltvshows": # Number of TV Shows
        if filteryear != "All":
            result = cursor.execute("""SELECT COUNT(*) AS num_tv_shows
                                        FROM 'Netflix'
                                        WHERE type = 'TV Show' and release_year={};""".format(filteryear))
        else:
            result = cursor.execute("""SELECT COUNT(*) AS num_tv_shows
                                        FROM 'Netflix'
                                        WHERE type = 'TV Show';""")
        return result.fetchall()[0][0]
    
    # ======= Columns with comma seperated values would use pandas =========
    elif plot == "genres": # Number of Unique Genres
        genres_df = data['listed_in'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).reset_index(name='genre')
        genre_counts = genres_df['genre'].value_counts().reset_index(name='count')

        return len(genre_counts)

    elif plot == "directors": # Number of Directors
        casts_df = data['director'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).reset_index(name='director')
        all_casts = casts_df['director'].value_counts().reset_index(name='count')

        return len(all_casts)
    
    elif plot == "countries": # Number of Countries Represented
        country_df = data['country'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).reset_index(name='country')
        country_casts = country_df['country'].value_counts().reset_index(name='count')

        return len(country_casts)

# ========= Row 2: Pie, Wordcloud =========
def pie_chart(cursor,filteryear):
    # Data
    if filteryear != "All":
        result = cursor.execute("""SELECT type, COUNT(*) AS count   
                                    FROM "Netflix"
                                    WHERE release_year={}
                                    GROUP BY type;
                                    """.format(filteryear))
    else:
        result = cursor.execute("""SELECT type, COUNT(*) AS count   
                                    FROM "Netflix"
                                    GROUP BY type;
                                    """)
    pie_data = pd.Series({t[0]: t[1] for t in result.fetchall()})

    # Plots
    fig = px.pie(pie_data, values=pie_data.values, names=pie_data.index, color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_layout(width=300, height=300)
    st.plotly_chart(fig, use_container_width=True)

def wordcloud(data):
    # Data
    all_descriptions = ' '.join(data['description'].astype(str))
    # Plot
    wordcloud = WordCloud(width=800, height=400,
                      stopwords=STOPWORDS.update({"find","life"}), max_words=100, background_color='black', colormap='Reds', contour_color='black', contour_width=1).generate(all_descriptions)

    # Display the word cloud using matplotlib
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(use_container_width=True)

# ===== Row 3: Ratings, Show Additons =====
def rating_bar(data):
    # Data
    ratings = data.groupby(['rating_names', 'type']).size().reset_index(name='count')
    # Plot
    fig = px.bar(ratings, x='rating_names', y='count', color='type',
                labels={'count': 'Count of Shows','rating_names': 'Rating Names'},
                barmode='group',color_discrete_sequence=px.colors.sequential.RdBu)  # Use 'barmode' to group bars by 'type'
    st.plotly_chart(fig, use_container_width=True)

def show_additions(data):
    # Data
    data['date_added'] = pd.to_datetime(data['date_added'])
    data['month_added'] = data['date_added'].dt.to_period('M')
    # Group by month and count the number of shows added
    monthly_counts = data['month_added'].value_counts().sort_index().reset_index()
    monthly_counts['month_added'] = monthly_counts['month_added'].astype(str)

    # Plot
    fig = px.line(monthly_counts, x='month_added', y='count', labels={'month_added': 'Number of Shows Added', 'index':'Years'},
                color_discrete_sequence=px.colors.sequential.RdBu)

    st.plotly_chart(fig, use_container_width=True)

# ======= Row 4: Casts, Directors =========
def casts_bar(data):
    # Data
    casts_df = data['cast'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).reset_index(name='cast')
    top_casts = casts_df['cast'].value_counts().reset_index(name='count').head(20)
    # Plot
    fig = px.bar(top_casts, x='cast', y='count',
             labels={'count': 'Number of Shows','index': 'Actors'},
             color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)

def directors_bar(data):
    # Data
    casts_df = data['director'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).reset_index(name='director')
    # Group by cast and count by top 20
    top_casts = casts_df['director'].value_counts().reset_index(name='count').head(20)

    # Plot
    fig = px.bar(top_casts, x='director', y='count',
             labels={'count': 'Number of Shows','index': 'Directors'},
             color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)

# ============ Row 5: Tree map ============
def tree_map(data):
    genres_df = data['listed_in'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).reset_index(name='genre')
    # Merge the new DataFrame with the original one
    df_merged = pd.merge(data, genres_df, left_index=True, right_index=True)

    # Create a Treemap chart using Plotly Express
    fig = px.treemap(df_merged, path=['type', 'genre'], color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)

# ============== Row 6: Map ===============
def country_map(data):
    country_counts = data['main_country'].value_counts().reset_index(name='count')

    # Create a Choropleth map using Plotly Express
    fig = px.choropleth(country_counts, locations='main_country', locationmode='country names',
                        color='count', hover_name='main_country', color_continuous_scale='Inferno')
    st.plotly_chart(fig, use_container_width=True)
