import difflib
import json
import re
import itertools
import ast
from functools import wraps

import pandas as pd
from flask import Flask
from flask import request
from flask_restplus import Resource, Api
from flask_restplus import abort
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse


pd.options.mode.chained_assignment = None

#reading csv file, assuming we are using the dataset from kaggle
def read_csv(file):
    #if the file is tmdb_5000
    if file == 'tmdb_5000_movies.csv':
        df = pd.read_csv(file)
        df = extract_tmdb_5000_Columns(df)

    return df

#extracting columns from tmdb 5000 csv file
def extract_tmdb_5000_Columns(df):

    df = df[['title','tagline', 'overview', 
            'release_date', 'popularity', 'genres', 'keywords',
            'spoken_languages', 'production_companies', 'production_countries',
            'vote_average', 'vote_count']]

    #preprocess and renaming variable
    df['production_countries'] = df['production_countries'].str.replace('iso_3166_1', 'abbrev')
    df['spoken_languages'] = df['spoken_languages'].str.replace('iso_639_1', 'abbrev')
    df['spoken_languages'] = df['spoken_languages'].str.replace('", "name":.*},', '"},')
    df['spoken_languages'] = df['spoken_languages'].str.replace('", "name":.*}]', '"}]')
    df.reset_index()
    df.index.name="index"
    return df

#Displaying columns with percentage of nulls
def display_percentage_of_nulls(df):
    num_of_rows = df.shape[0]
    for column in df:
        percent = 100 * df[column].isnull().sum() / num_of_rows
        print(column, str(percent) + '%')

def isNaN(num):
    return num != num

#Query
#By title
def get_movies_by_title(df, title):
    return df.loc[df['title'].str.contains(title, flags=re.IGNORECASE)]

def get_movies_by_exact_title(df, title):
    return df.loc[df['title'] == title]

#By release date
def get_movies_by_release_date(df, date):
    return df.loc[df['release_date'] == date]

#By genre
def get_movies_by_genre(df, genre):
    return df[df['genres'].str.contains(genre, flags=re.IGNORECASE)]

#By list of genres (Only movie that satisfy all genres will return)
def get_movies_by_list_of_genres(df, genres):
    df1 = df 
    for g in genres:
        df1 = df1[df1['genres'].str.contains(g)]
    return df1

#By keyword
def get_movies_by_keyword(df, keyword):
    return df[df['keywords'].str.contains(keyword, flags=re.IGNORECASE)]

#By list of keywords
def get_movies_by_list_of_keywords(df, keywords):
    df1 = df
    for k in keywords:
        df1 = df1[df1['keywords'].str.contains(k, flags=re.IGNORECASE)]
    return df1

#By language
def get_movies_by_language(df, language, ln):
    if len(language) > 2:
        #ln = ln[ln['full'].str.contains(language)]
        for index, row in ln[ln['full'].str.contains(language)].iterrows():
            shortForm = row['abb']
            return df[df['spoken_languages'].str.contains('"' + shortForm + '"')]         
    else:
        return df[df['spoken_languages'].str.contains('"' + language + '"')] 


#By country
def get_movies_by_country(df, country):
    if len(country) > 2:
        return df[df['production_countries'].str.contains(country)] 
    else :
        return df[df['production_countries'].str.contains('"' + country + '"')] 

#By list of countries
def get_movies_by_list_of_countries(df, countries):
    df1 = df    
    for country in countries:
        if len(country) > 2:
            df1 = df1[df1['production_countries'].str.contains(country)]
        else:
            df1 = df1[df1['production_countries'].str.contains('"' + country + '"')]
    return df1

#By company
def get_movies_by_company(df, company):
    return df[df['production_companies'].str.contains(company)]

def get_movies_by_list_of_companies(df, companies):
    df1 = df     
    for c in companies:
        df1 = df1[df1['production_companies'].str.contains(company)]
    return df1 

def get_ids(ss):
    ids = []
    dict_list = json.loads(ss)

    for d in dict_list:
        for key, value in d.items():
            if key == 'id':
                ids.append(value)

    return ids

def get_values(ss):
    if isNaN(ss) or ss is None:
        return None

    values = []
    #print(type(ss))
    dict_list = json.loads(ss)
    #print(type(ss))
    for d in dict_list:
        for key, value in d.items():
            if key == 'name':
                values.append(value)

    return values

def get_string_match(m1, m2, check_ids=True):
    match = 0
    curr_movie = get_ids(m1) if check_ids else get_values(m1)
    target_movie = get_ids(m2) if check_ids else get_values(m2)

    if (check_ids):
        for x in target_movie:
            for y in curr_movie:
                if x == y:
                    match += 1
    else:
        for x in target_movie:
            for y in curr_movie:
                if y.contains(x, flags=re.IGNORECASE):
                    match += 1

    return match

def get_rating_match(m1, m2):
    if isNaN(m1) or isNaN(m2):
        return 0
    curr_rating = int(m1)
    target_rating = int(m2)
    return curr_rating-target_rating


def get_date_match(m1, m2):
    if isNaN(m1) or isNaN(m2):
        return 0
    curr_year = int(m1[0:4])
    target_year = int(m2[0:4])
    return curr_year-target_year


def get_popularity_match(m1, m2):
    if isNaN(m1) or isNaN(m2):
        return 0
    curr_popularity = float(m1)
    target_popularity = float(m2)
    return curr_popularity-target_popularity

def get_correlation_score_in_genre(df, genre, check_ids=True):
    df1 = df
    df1['genre_match_score'] = df1['genres'].apply(lambda x: get_string_match(x, genre, check_ids))
    return df1

def get_correlation_score_in_rating(df, voting_average):
    df1 = df
    df1['rating_score'] = df1['vote_average'].apply(lambda x: get_rating_match(x, voting_average))
    return df1

def get_correlation_score_in_keyword(df, keywords, check_ids=True):
    df1 = df
    df1['keyword_score'] = df1['keywords'].apply(lambda x: get_string_match(x, keywords, check_ids))
    return df1

def get_correlation_score_in_date(df, release_date):
    df1 = df
    df1['date_score'] = df1['release_date'].apply(lambda x: get_date_match(x, release_date))
    return df1

def get_correlation_score_in_popularity(df, popularity):
    df1 = df
    df1['popularity_score'] = df1['popularity'].apply(lambda x: get_popularity_match(x, popularity))
    #print(df1['popularity_score'])
    return df1

def get_correlation_score_with_other_movies(df, movie):
    genre_correlation = get_correlation_score_in_genre(df, movie['genres'].item())
    rating_correlation = get_correlation_score_in_rating(genre_correlation, movie['vote_average'].item())
    keyword_correleation = get_correlation_score_in_keyword(rating_correlation, movie['keywords'].item())
    popularity_correlation = get_correlation_score_in_popularity(keyword_correleation, movie['popularity'].item())
    df1 = get_correlation_score_in_date(popularity_correlation, movie['release_date'].item())

    df1['final_correlation'] = (df1['genre_match_score']*5) + df1['rating_score'] + (df1['keyword_score']*5) + (df1['popularity_score']/50)
    #print(df.iloc[df1['final_correlation'].sort_values(ascending=False).index].head(10))
    return df1

#ADD DATAFRAME TO DB (OPTIONAL)
def add_data_to_db(df, name):
    db_name = 'comp9321asst2'
    mongo_port = 27017
    mongo_host = 'localhost'

    client = MongoClient(mongo_host, mongo_port)
    db = client[db_name]
    c = db[name]
    records = json.loads(df.T.to_json()).values()
    c.insert(records)

def write_json_obj(df1):
    json_str = df1.to_json(orient='index')

    ds = json.loads(json_str)
    ret = []

    for idx in ds:
        # print(idx)
        movie = ds[idx]
        movie['index'] = int(idx)
        ret.append(movie)

    return ret
###########
#API
###########
app = Flask(__name__)
api = Api(app,
          default = "Movies",
          title="Movie Dataset",
          description="This is the movie recommender Anna")


#movie_model = api.model('Movie', {
#    'Title': fields.String,
#    'Genre': fields.String,
#    'Country': fields.String,
#    'Keyword': fields.String,
#    'Date': fields.String,
#    'Language': fields.String,
#    'Company': fields.String
#})

@api.route('/movies')
class MovieList(Resource):

    @api.response(200, 'Successful')
    @api.doc(description="Get all movies")
    def get(self):
        
        json_str = df.to_json(orient='index')

        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            #print(idx)
            movie = ds[idx]
            movie['index'] = int(idx)
            ret.append(movie)

        return ret 

@api.route('/movies/<string:name>')
@api.param('name', 'The name of movie')
class Movie(Resource):
    @api.response(404, 'Movie was not found')
    @api.response(200, 'Successful')
    @api.doc(description="Get a book by its ID")
    def get(self, name):
        
        rdf = get_movies_by_title(df, str(name))

        if rdf.empty:
            api.abort(404, "Movie {} not found".format(name))
        else:
            json_str = rdf.to_json(orient='index')

            ds = json.loads(json_str)
            ret = []

            for idx in ds:
                #print(idx)
                movie = ds[idx]
                movie['index'] = int(idx)
                ret.append(movie)

            return ret 
        

    #@api.response(201, 'Movie Added Successfully')
    #@api.response(400, 'Validation Error')
    #@api.doc(description="Add a new movie")
    #def post(self):
    #    pass


@api.route('/movie-recommendation')
@api.param('name', 'The name of movie the person likes, the recommendation would be different to this movie')
@api.param('rating', 'Minimum rating of the movie the person would want to see in the recommendation')
@api.param('year', 'Minimum year of the release year of the movie')
@api.param('genre', 'Genre of the movie the person would like')
class MovieRecommendation(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Get a book by its ID")
    def get(self):

        name = request.args.get('name', None)
        rating = request.args.get('rating', None)
        year = request.args.get('year', None)
        genre = request.args.get('genre', None)

        print("NAME = ", name)
        print("RATING = ", rating)
        print("GENRE = ", genre)
        print("YEAR = ", year)

        final_df = pd.DataFrame()

        # By Movie Name
        if name is not None:
            movies = get_movies_by_title(df, str(name))
            closest_matches = difflib.get_close_matches(str(name), movies['title'], cutoff=0.1)

            closest_match = ''
            if len(closest_matches) > 1:
                closest_match = closest_matches[0]
            else:
                pass
                #  No match, just choose random

            movie = get_movies_by_exact_title(df, str(closest_match))

            if movie.empty:
                api.abort(404, "Movie {} not found".format(name))

            df1 = get_correlation_score_with_other_movies(df, movie).head(10)
            final_df = df1

        # By Genre
        if genre is not None:
            print("In Genre")
            genres = []
            for curr_genre in df['genres']:
                genres.append(get_values(curr_genre))
                pass

            unique_genres = set(list(itertools.chain.from_iterable(genres)))

            closest_matches = difflib.get_close_matches(str(genre), unique_genres, cutoff=0.1)

            #print(closest_matches)
            if len(closest_matches) > 1:
                closest_match = closest_matches[0]
            else:
                api.abort(404, "Genre {} not found in movies".format(genre))
                pass

            df2 = get_movies_by_genre(df, closest_match)
            #print(df2.sort_values(['popularity'], ascending=False).head(10))

            if final_df.empty:
                final_df = df2
            else:
                final_df.append(df2)

        # By Rating
        if rating is not None:
            print('In Rating')
            df3 = df[(df['vote_average'] >= float(rating)-1) & (df['vote_average'] <= float(rating)+1)].sort_values(['popularity'], ascending=False).head(10)
            if final_df.empty:
                final_df = df3
            else:
                final_df.append(df3)

        # By Year
        if year is not None:
            print('IN YEAR')
            df4 = df
            df4['date_match'] = df4['release_date'].apply(lambda x: get_date_match(x, year))
            df4 = df.iloc[df4[(df4['date_match'] >= -1) & (df4['date_match'] <= 1)].sort_values(['popularity'], ascending=False).index].head(10)
            #print(df4)
            if final_df.empty:
                final_df = df4
            else:
                final_df.append(df4)

        final_df = final_df.sort_values(['popularity', 'vote_average'], ascending=False).head(10)
        print(final_df)
        return write_json_obj(final_df)

if __name__ == "__main__":
    csv_file = "tmdb_5000_movies.csv"
    df = read_csv(csv_file)
    #dict of language abbrevation and its long form
    ln = pd.read_csv("languages.csv")

    app.run(debug=True)