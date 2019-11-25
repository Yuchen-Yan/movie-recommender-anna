import json

import pandas as pd
from flask import Flask
from flask import request
from flask_restplus import Resource, Api
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

#Query
#By title
def get_movies_by_title(df, title):
    return df.loc[df['title'] == title]

#By release date
def get_movies_by_release_date(df, date):
    return df.loc[df['release_date'] == date]

#By genre
def get_movies_by_genre(df, genre):
    return df[df['genres'].str.contains(genre)]

#By list of genres (Only movie that satisfy all genres will return)
def get_movies_by_list_of_genres(df, genres):
    df1 = df 
    for g in genres:
        df1 = df1[df1['genres'].str.contains(g)]
    return df1

#By keyword
def get_movies_by_keyword(df, keyword):
    return df[df['keywords'].str.contains(keyword)]

#By list of keywords
def get_movies_by_list_of_keywords(df, keywords):
    df1 = df
    for k in keywords:
        df1 = df1[df1['keywords'].str.contains(k)]
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

###########
#API
###########


app = Flask(__name__)
api = Api(app,
          default = "Movies",
          title="Movie Dataset",
          description="This is the movie recommender Anna")

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
    @api.response(404, 'Book was not found')
    @api.response(200, 'Successful')
    @api.doc(description="Get a book by its ID")
    def get(self, name):
        
        rdf = get_movies_by_title(df, str(name))

        if rdf.empty:
            pass
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


if __name__ == "__main__":
    csv_file = "tmdb_5000_movies.csv"
    df = read_csv(csv_file)
    #dict of language abbrevation and its long form
    ln = pd.read_csv("languages.csv")

    app.run(debug=True)