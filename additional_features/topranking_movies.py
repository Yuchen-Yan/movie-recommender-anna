import pandas as pd
import numpy as np


##################load the data and merge together##################
df1=pd.read_csv('tmdb_5000_credits.csv')
df2=pd.read_csv('tmdb_5000_movies.csv')

df1.columns = ['id','tittle','cast','crew']
df2= df2.merge(df1,on='id')


#####average rating#####
C = df2['vote_average'].mean()

#####vote average quantile#####
m = df2['vote_count'].quantile(0.9)

###movie that qualified###
q_movies = df2.copy().loc[df2['vote_count'] >= m]

#####A function that#####
def weighted_rating(x, m=m, C=C):
    v = x['vote_count']
    R = x['vote_average']
    # Calculation based on the IMDB formula
    return (v/(v+m) * R) + (m/(m+v) * C)


# Define a new feature 'score' and calculate its value with `weighted_rating()`
q_movies['score'] = q_movies.apply(weighted_rating, axis=1)

#Sort movies based on score calculated above
q_movies = q_movies.sort_values('score', ascending=False)

#Print the top 15 movies
print(q_movies[['title', 'vote_count', 'vote_average', 'score']].head(10))



