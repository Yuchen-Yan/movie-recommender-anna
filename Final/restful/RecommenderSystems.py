import pandas as pd
import numpy as np


def init():
    df_rating = pd.read_csv('processdata/ratings.csv')
    df_movie = pd.read_csv('processdata/movies.csv')
    return process_movie_data(df_movie), df_rating 

def process_movie_data (movies):
    #movies['title'] = movies['title'].str.replace(' (\d{4})$', '')
    movies['title'] = movies['title'].str.replace(' \(\d{4}\)', '')
    return movies

def constructUserMovieMatrix(df_movie, df_rating):
    df = pd.merge(df_rating, df_movie, on='movieId')
    movie_matrix = df.pivot_table(index = 'userId', columns = 'title', values = 'rating')
    return movie_matrix, df

def calculationSimilarity(data_matrix, title):
    movie_user_rating = data_matrix[title]
    simliar_to_movie = data_matrix.corrwith(movie_user_rating)
    return simliar_to_movie

def linkswithTMDB(result, df_movie):
    df_links = pd.read_csv('processdata/links.csv')
    df = pd.merge(result, df_movie, on='title')
    df2 =  pd.merge(df, df_links, on='movieId')
    df2.drop(['movieId','title','number_of_ratings', 'genres', 'imdbId'],inplace=True, axis=1)

    return df2.head(10)

def Recommender(title):
    df_movie, df_rating = init()
    movie_matrix, df = constructUserMovieMatrix(df_movie, df_rating)

    simliar_to_movie = calculationSimilarity(movie_matrix, title)

    corr_movie = pd.DataFrame(simliar_to_movie, columns = ['Correlation'])
    corr_movie.dropna(inplace = True) # remove NaN

    ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
    ratings['number_of_ratings'] = df.groupby('title')['rating'].count()

    corr_movie = corr_movie.join(ratings['number_of_ratings'],how = 'left',lsuffix='_left', rsuffix='_right')
    result = corr_movie[corr_movie['number_of_ratings']>100].sort_values(by = 'Correlation', ascending = False)
    return linkswithTMDB(result, df_movie)
