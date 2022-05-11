import streamlit as st
import pandas as pd

movies = pd.read_csv(r'ml-latest-small\movies.csv')
ratings = pd.read_csv(r'ratings.csv')
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
def get_sparse_matrix(dense_matrix: pd.DataFrame):
    sparse_matrix = (dense_matrix.pivot(index='userId', columns='movieId', values='rating'))
    return sparse_matrix
def item_based_recommender(dense_matrix: pd.DataFrame, movieId: int, n: int):
    sparse_matrix = get_sparse_matrix(dense_matrix)
    correlation = (sparse_matrix
                 .corrwith(sparse_matrix[movieId])
                 .sort_values(ascending=False)[1:n+1]
                 .reset_index())
    correlation_title = correlation.merge(movies, how='left', on='movieId')[['title', 'genres']]
    return correlation_title

st.title("Movie Recommendation")
 
st.write("""This will recommend you the bestest movies ever.""")

selected_movie = st.text_input('Just type in a movie you like:')

recommended_movies = item_based_recommender(ratings_item, selected_movie, 10)

st.write("You might also enjoy watching:", recommended_movies)