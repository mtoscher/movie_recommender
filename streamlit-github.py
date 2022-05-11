import streamlit as st
import pandas as pd
import numpy as np

movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')
ratings_item = ratings.merge(movies, how='left', on='movieId')
ratings_grpd = ratings_item.groupby('movieId').agg(title_grpd = ('title', 'min'), count_ratings = ('rating', 'count')).reset_index()
movies_duplicates = ratings_grpd[ratings_grpd['title_grpd'].duplicated()]['title_grpd'].to_list()
movies_duplicates_enr = pd.DataFrame(columns=ratings_grpd.columns)
for m in movies_duplicates:
    rating_m = ratings_grpd[ratings_grpd.title_grpd == m].sort_values(by=['title_grpd', 'count_ratings'], ascending=False)
    movies_duplicates_enr = movies_duplicates_enr.append(rating_m, ignore_index=True)
for i in range(1, len(movies_duplicates_enr), 2):
    ratings_item.loc[(ratings_item.movieId == movies_duplicates_enr["movieId"][i]), 'movieId'] = movies_duplicates_enr["movieId"][i-1]
duplicated2 = ratings_item.duplicated(subset=['userId', 'title']).to_frame(name='duplicate').query('duplicate == True').index.to_list()
ratings_item = ratings_item.drop(duplicated2).reset_index()
movies_vfew_ratings = ratings_item.groupby('movieId').agg(rating_count=('rating', 'count')).sort_values(by='rating_count').query('rating_count < 5').reset_index().index.to_list()
ratings_item = ratings_item.drop(movies_vfew_ratings)

st.title("Movie Recommendation")
 
st.write("""This will recommend you the bestest movies ever.""")

preferred_movie_title = st.selectbox(label='Select a movie you like and press enter', options=np.sort(ratings_item['title'].unique()))

number_of_recommendations = st.number_input(label='Select the number of movie recommendations and press enter', min_value=1, max_value=50)

preferred_movie_id = ratings_item.query('title == @preferred_movie_title').reset_index()['movieId'][0]

sparse_matrix = ratings_item.pivot(index='userId', columns='movieId', values='rating')
correlation = (sparse_matrix
                 .corrwith(sparse_matrix[preferred_movie_id])
                 .sort_values(ascending=False)[1:number_of_recommendations+1]
                 .reset_index())

correlation_title = correlation.merge(movies, how='left', on='movieId')[['title', 'genres']]

st.write("You might also enjoy watching:")
st.table(correlation_title)