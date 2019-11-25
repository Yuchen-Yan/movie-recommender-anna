import pandas as pd
import numpy as np
import sys

title = sys.argv[1]


df_rating = pd.read_csv('processdata/ratings.csv')
df_movie = pd.read_csv('processdata/movies.csv')

df = pd.merge(df_rating, df_movie, on='movieId')
movie_matrix = df.pivot_table(index = 'userId', columns = 'title', values = 'rating')

movie_user_rating = movie_matrix[title]
simliar_to_movie = movie_matrix.corrwith(movie_user_rating)

corr_movie = pd.DataFrame(simliar_to_movie, columns = ['Correlation'])
corr_movie.dropna(inplace = True) # remove NaN

ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
ratings['number_of_ratings'] = df.groupby('title')['rating'].count()

corr_movie = corr_movie.join(ratings['number_of_ratings'],how = 'left',lsuffix='_left', rsuffix='_right')
reusult = corr_movie[corr_movie['number_of_ratings']>100].sort_values(by = 'Correlation', ascending = False)
print(reusult)